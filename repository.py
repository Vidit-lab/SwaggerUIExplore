"""The storage seam. Routes depend on TaskRepository, never on SQL directly —
swapping the backend again means writing a new class here, not touching main.py.
"""

import os
from typing import Protocol

import psycopg
from psycopg.rows import class_row

from models import Task

DATABASE_URL = os.environ["DATABASE_URL"]


class TaskRepository(Protocol):
    def list_all(self) -> list[Task]: ...
    def get(self, task_id: int) -> Task | None: ...
    def create(self, title: str) -> Task: ...
    def update(self, task_id: int, fields: dict) -> Task | None: ...
    def delete(self, task_id: int) -> bool: ...


class PostgresTaskRepository:
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def list_all(self) -> list[Task]:
        with self.conn.cursor(row_factory=class_row(Task)) as cur:
            return cur.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()

    def get(self, task_id: int) -> Task | None:
        with self.conn.cursor(row_factory=class_row(Task)) as cur:
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
            return cur.fetchone()

    def create(self, title: str) -> Task:
        with self.conn.cursor(row_factory=class_row(Task)) as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, FALSE) RETURNING id, title, done",
                (title,),
            )
            return cur.fetchone()

    def update(self, task_id: int, fields: dict) -> Task | None:
        # Column names come from TaskUpdate's own fields, never from the request body,
        # so this interpolation cannot carry user input. Values stay parameterised.
        assignments = ", ".join(f"{column} = %s" for column in fields)
        with self.conn.cursor(row_factory=class_row(Task)) as cur:
            cur.execute(
                f"UPDATE tasks SET {assignments} WHERE id = %s RETURNING id, title, done",
                (*fields.values(), task_id),
            )
            return cur.fetchone()

    def delete(self, task_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return cur.rowcount > 0


def get_repository():
    # One connection per request, committed on a clean exit. ponytail: no pool,
    # add psycopg_pool.ConnectionPool if this needs to handle real concurrency.
    with psycopg.connect(DATABASE_URL) as conn:
        yield PostgresTaskRepository(conn)
