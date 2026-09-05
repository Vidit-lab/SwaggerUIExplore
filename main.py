from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints

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


app = FastAPI(title="Task API", version="1.0")

# Our "database": a plain list. It resets every time the server restarts.
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


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks() -> list[Task]:
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> Task:
    return find(task_id)


@app.post("/tasks", status_code=201)
def create_task(new: TaskCreate) -> Task:
    task = Task(id=max((t.id for t in tasks), default=0) + 1, title=new.title, done=False)
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, changes: TaskUpdate) -> Task:
    task = find(task_id)
    fields = changes.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "Send at least one of: title, done")
    for name, value in fields.items():
        setattr(task, name, value)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    tasks.remove(find(task_id))
