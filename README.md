# Task API

A small CRUD API for a to-do list, built with [FastAPI](https://fastapi.tiangolo.com/)
and stored in a **SQLite** database. The endpoints behave exactly as they did when
the tasks lived in a Python list — the difference is that the data now survives a
restart.

```
Client  ->  FastAPI  ->  SQLite (tasks.db)
```

## Install & run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install "fastapi[standard]"
fastapi dev main.py
```

That is the whole setup. The server comes up on <http://localhost:8000> with
Swagger UI at <http://localhost:8000/docs>, and **the database creates itself** on
first start — there is nothing to install, migrate or seed by hand.

Run the self-check with `python test_api.py`; it prints `ok`. It exercises the
whole CRUD cycle, every status code, and the restart-persistence guarantee,
against a throwaway database in a temp directory rather than your real one.

## Why SQLite

- **No server to run.** Postgres or MySQL would mean a daemon, a port, a user and
  a password before a single row exists. SQLite is a C library reading one file.
- **The database is the file.** `tasks.db` can be copied, deleted or inspected
  with any editor, which makes it easy to see what the API actually wrote.
- **It is already installed.** Python ships the `sqlite3` module in its standard
  library, so this project still has exactly one dependency: FastAPI.
- **It is real SQL.** The same `SELECT`/`INSERT`/`UPDATE`/`DELETE` statements
  transfer to a bigger database later. Nothing learned here is throwaway.

## Where the database lives

A single file named `tasks.db`, in the directory you start the server from — the
repository root, if you follow the command above. It is created on first startup,
along with the `tasks` table:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY,
    title TEXT    NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT 0
);
```

Three example tasks are inserted **only when the table is empty**, so restarting
the server never duplicates them. `tasks.db` is in `.gitignore`: it is generated
data, not source, and a fresh clone rebuilds it on the first run.

To point the app at a different file, set `TASKS_DB=/some/other.db`.

## Endpoints

| Method | Path | Does | Success | Errors |
| --- | --- | --- | --- | --- |
| GET | `/` | Describes the API | 200 | — |
| GET | `/health` | Liveness check | 200 | — |
| GET | `/tasks` | List every task | 200 | — |
| GET | `/tasks/{id}` | One task by id | 200 | 404 unknown id |
| POST | `/tasks` | Create a task from `{"title": "..."}` | 201 | 400 missing/empty title |
| PUT | `/tasks/{id}` | Update `title` and/or `done` | 200 | 400 empty body · 404 unknown id |
| DELETE | `/tasks/{id}` | Remove a task (empty body) | 204 | 404 unknown id |

A task looks like `{"id": 1, "title": "Read the FastAPI docs", "done": true}`.
Every error comes back as JSON: `{"error": "Task 99 not found"}`.

## Example: the full cycle with `curl -i`

```console
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
HTTP/1.1 201 Created
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}

$ curl -i http://localhost:8000/tasks/99
HTTP/1.1 404 Not Found
content-length: 29
content-type: application/json

{"error":"Task 99 not found"}

$ curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d '{"done":true}'
HTTP/1.1 200 OK
content-length: 39
content-type: application/json

{"id":4,"title":"Buy milk","done":true}

$ curl -i -X DELETE http://localhost:8000/tasks/4
HTTP/1.1 204 No Content
content-type: application/json

$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{}'
HTTP/1.1 400 Bad Request
content-length: 33
content-type: application/json

{"error":"title: Field required"}
```

## Swagger UI

FastAPI builds the OpenAPI spec from the type hints in [main.py](main.py), so
`/docs` needs no setup — every endpoint is listed with its schema and a
**Try it out** button that sends real requests. The whole CRUD cycle below was
run from that page, no curl involved.

**Create** — `POST /tasks` with `{"title": "Buy milk"}` returns **201** and the new task:

![POST /tasks returning 201 Created](docs/Post.png)

**Read all** — `GET /tasks` returns **200** and the list, now four tasks long:

![GET /tasks returning 200 and the task list](docs/Get.png)

**Read one** — `GET /tasks/4` returns **200** and the single task:

![GET /tasks/4 returning 200 and one task](docs/Get_task.png)

**Update** — `PUT /tasks/4` returns **200** and the task with `done` flipped to true:

![PUT /tasks/4 returning 200 and the updated task](docs/Put.png)

**Delete** — `DELETE /tasks/4` returns **204** with an empty body:

![DELETE /tasks/4 returning 204 No Content](docs/Delete.png)

