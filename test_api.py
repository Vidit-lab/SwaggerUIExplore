"""One runnable check of the whole CRUD cycle: python test_api.py"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_crud_cycle():
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

    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert len(client.get("/tasks").json()) == 3


def test_errors():
    missing = client.get("/tasks/99")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Task 99 not found"}

    for bad_body in ({}, {"title": "   "}):
        assert client.post("/tasks", json=bad_body).status_code == 400
    assert client.put("/tasks/1", json={}).status_code == 400
    assert client.put("/tasks/99", json={"done": True}).status_code == 404
    assert client.delete("/tasks/99").status_code == 404


if __name__ == "__main__":
    test_crud_cycle()
    test_errors()
    print("ok")
