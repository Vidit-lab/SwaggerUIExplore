"""Task API — a small CRUD to-do list stored in Postgres. Swagger UI lives at /docs."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from models import Task, TaskCreate, TaskUpdate
from repository import TaskRepository, get_repository

Repo = Annotated[TaskRepository, Depends(get_repository)]

app = FastAPI(
    title="Task API",
    version="3.0",
    description="Create, read, update and delete to-do tasks, stored in Postgres "
    "behind a repository interface — the routes below don't know it's SQL.",
)


def find(repo: TaskRepository, task_id: int) -> Task:
    task = repo.get(task_id)
    if task is None:
        raise HTTPException(404, f"Task {task_id} not found")
    return task


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
def list_tasks(repo: Repo) -> list[Task]:
    return repo.list_all()


@app.get("/tasks/{task_id}", summary="Get one task by id (404 if there is none)")
def get_task(task_id: int, repo: Repo) -> Task:
    return find(repo, task_id)


@app.post("/tasks", status_code=201, summary="Create a task from a title")
def create_task(new: TaskCreate, repo: Repo) -> Task:
    return repo.create(new.title)


@app.put("/tasks/{task_id}", summary="Update a task's title and/or done flag")
def update_task(task_id: int, changes: TaskUpdate, repo: Repo) -> Task:
    find(repo, task_id)
    fields = changes.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "Send at least one of: title, done")
    return repo.update(task_id, fields)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task, returning no body")
def delete_task(task_id: int, repo: Repo) -> None:
    if not repo.delete(task_id):
        raise HTTPException(404, f"Task {task_id} not found")
