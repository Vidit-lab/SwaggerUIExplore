"""One runnable check of the whole CRUD cycle: python test_api.py

Needs a reachable Postgres — run `docker compose up -d db` first. Defaults to
the port docker-compose.yml publishes to the host; override with DATABASE_URL.
It cleans up the row it creates, so it's safe to run against a shared dev database.
"""

import os

os.environ.setdefault("DATABASE_URL", "postgresql://taskapi:taskapi@localhost:5433/tasks")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_crud_cycle():
    before = len(client.get("/tasks").json())

    created = client.post("/tasks", json={"title": "Buy milk"})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Buy milk" and task["done"] is False
    task_id = task["id"]

    assert client.get(f"/tasks/{task_id}").json() == task
    assert len(client.get("/tasks").json()) == before + 1

    updated = client.put(f"/tasks/{task_id}", json={"done": True})
    assert updated.status_code == 200
    assert updated.json()["done"] is True
    assert client.get(f"/tasks/{task_id}").json()["done"] is True

    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert len(client.get("/tasks").json()) == before


def test_errors():
    missing = client.get("/tasks/999999")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Task 999999 not found"}

    for bad_body in ({}, {"title": "   "}):
        assert client.post("/tasks", json=bad_body).status_code == 400

    created = client.post("/tasks", json={"title": "temp"}).json()
    assert client.put(f"/tasks/{created['id']}", json={}).status_code == 400
    client.delete(f"/tasks/{created['id']}")

    assert client.put("/tasks/999999", json={"done": True}).status_code == 404
    assert client.delete("/tasks/999999").status_code == 404


def test_a_failed_request_writes_nothing():
    before = client.get("/tasks/1").json()
    assert client.put("/tasks/1", json={"title": ""}).status_code == 400
    assert client.get("/tasks/1").json() == before


if __name__ == "__main__":
    test_crud_cycle()
    test_errors()
    test_a_failed_request_writes_nothing()
    print("ok")
