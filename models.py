"""Request/response shapes, shared by the routes and every repository implementation."""

from typing import Annotated

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
