"""One runnable check of the whole CRUD cycle: python test_api.py

Points TASKS_DB at a throwaway file first, so running this never touches tasks.db.
"""

import os
import tempfile

os.environ["TASKS_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


def test_crud_cycle():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert len(client.get("/tasks").json()) == 3

        created = client.post("/tasks", json={"title": "Buy milk"})
        assert created.status_code == 201
        task = created.json()
        assert task == {"id": 4, "title": "Buy milk", "done": False}

        assert client.get(f"/tasks/{task['id']}").json() == task

        updated = client.put(f"/tasks/{task['id']}", json={"done": True})
        assert updated.status_code == 200
        assert updated.json()["done"] is True
        assert client.get(f"/tasks/{task['id']}").json()["done"] is True

        assert client.delete(f"/tasks/{task['id']}").status_code == 204
        assert len(client.get("/tasks").json()) == 3


def test_survives_a_restart():
    with TestClient(app) as client:
        task_id = client.post("/tasks", json={"title": "Outlive the process"}).json()["id"]

    with TestClient(app) as client:  # a second startup, same database file
        assert client.get(f"/tasks/{task_id}").json()["title"] == "Outlive the process"
        assert client.delete(f"/tasks/{task_id}").status_code == 204


def test_errors():
    with TestClient(app) as client:
        missing = client.get("/tasks/99")
        assert missing.status_code == 404
        assert missing.json() == {"error": "Task 99 not found"}

        for bad_body in ({}, {"title": "   "}):
            assert client.post("/tasks", json=bad_body).status_code == 400
        assert client.put("/tasks/1", json={}).status_code == 400
        assert client.put("/tasks/99", json={"done": True}).status_code == 404
        assert client.delete("/tasks/99").status_code == 404


def test_a_failed_request_writes_nothing():
    with TestClient(app) as client:
        before = client.get("/tasks/1").json()
        assert client.put("/tasks/1", json={"title": ""}).status_code == 400
        assert client.get("/tasks/1").json() == before


if __name__ == "__main__":
    test_crud_cycle()
    test_survives_a_restart()
    test_errors()
    test_a_failed_request_writes_nothing()
    print("ok")
