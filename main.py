from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    done: bool


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
