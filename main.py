"""Task API — a small CRUD to-do list stored in SQLite. Swagger UI lives at /docs."""

import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints

# One file on disk, created on first run. The test suite points this elsewhere.
DB_FILE = os.environ.get("TASKS_DB", "tasks.db")

# A title that is missing, empty or only whitespace is rejected by the model.
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Task(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: Title


class TaskUpdate(BaseModel):
    title: Title | None = None
    done: bool | None = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY,
    title TEXT    NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT 0
)
"""

EXAMPLE_TASKS = [
    ("Read the FastAPI docs", 1),
    ("Build a CRUD API", 0),
    ("Push it to GitHub", 0),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the table on startup, and seed it only while it is still empty."""
    conn = sqlite3.connect(DB_FILE)
    with conn:
        conn.execute(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
            conn.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", EXAMPLE_TASKS)
    conn.close()
    yield


def get_db():
    """One connection per request, committed only if the endpoint returned cleanly."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


Db = Annotated[sqlite3.Connection, Depends(get_db)]

app = FastAPI(
    title="Task API",
    version="2.0",
    description="Create, read, update and delete to-do tasks. "
    "Everything is stored in a SQLite file, so the list survives a restart.",
    lifespan=lifespan,
)

# Still the in-memory list — the endpoints move onto SQL in the next stages.
tasks: list[Task] = [
    Task(id=1, title="Read the FastAPI docs", done=True),
    Task(id=2, title="Build a CRUD API", done=False),
    Task(id=3, title="Push it to GitHub", done=False),
]


def find(task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(404, f"Task {task_id} not found")


@app.exception_handler(HTTPException)
def error_response(request: Request, exc: HTTPException) -> JSONResponse:
    """Report errors as {"error": ...} instead of FastAPI's {"detail": ...}."""
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
def invalid_body(request: Request, exc: RequestValidationError) -> JSONResponse:
    """A body the models reject is a 400 here, not FastAPI's default 422."""
    problem = exc.errors()[0]
    field = ".".join(str(part) for part in problem["loc"][1:]) or "body"
    return JSONResponse({"error": f"{field}: {problem['msg']}"}, status_code=400)


@app.get("/", summary="What this API is")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Liveness check — is the server up?")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List every task")
def list_tasks() -> list[Task]:
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task by id (404 if there is none)")
def get_task(task_id: int) -> Task:
    return find(task_id)


@app.post("/tasks", status_code=201, summary="Create a task from a title")
def create_task(new: TaskCreate) -> Task:
    task = Task(id=max((t.id for t in tasks), default=0) + 1, title=new.title, done=False)
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}", summary="Update a task's title and/or done flag")
def update_task(task_id: int, changes: TaskUpdate) -> Task:
    task = find(task_id)
    fields = changes.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "Send at least one of: title, done")
    for name, value in fields.items():
        setattr(task, name, value)
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task, returning no body")
def delete_task(task_id: int) -> None:
    tasks.remove(find(task_id))
