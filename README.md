# Task API

A small CRUD API for a to-do list, built with [FastAPI](https://fastapi.tiangolo.com/)
and stored in **Postgres**, running in Docker alongside the app.

```
Client  ->  FastAPI (app container)  ->  Postgres (db container, named volume)
```

## Install & run

```bash
cp .env.example .env
docker compose up --build
```

One command starts both containers. The server comes up on
<http://localhost:8000>, with Swagger UI at <http://localhost:8000/docs>. The
database schema and three example tasks are created automatically the first
time the `db` volume is created — nothing to migrate or seed by hand.

Run the self-check with `python test_api.py` (needs `docker compose up -d db`
and the venv below); it prints `ok`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Why Postgres, in Docker

- **A real client/server database.** SQLite (used in the previous version of
  this project) is one file read by one process. Postgres is what production
  actually runs — a server, a network protocol, concurrent connections.
- **Docker instead of a local install.** `docker compose up` gives every
  contributor the same Postgres version with no install step and no
  system-wide service to manage or forget about.
- **A named volume, not a bind mount.** `pgdata:/var/lib/postgresql/data` in
  [docker-compose.yml](docker-compose.yml) is what makes the data outlive the
  container — `docker compose down && docker compose up` throws the
  containers away and rebuilds them from scratch, and the rows are still
  there. Proof is below.

## The repository seam — honestly

The previous version of this project (SQLite) had the routes in `main.py`
call `sqlite3` directly. Moving to Postgres was the moment to stop doing that:

- **[models.py](models.py)** — the `Task` / `TaskCreate` / `TaskUpdate` shapes,
  shared by the routes and every repository implementation.
- **[repository.py](repository.py)** — a `TaskRepository` `Protocol` (`list_all`,
  `get`, `create`, `update`, `delete`), and `PostgresTaskRepository`, the only
  implementation of it, built on [`psycopg`](https://www.psycopg.org/psycopg3/).
- **[main.py](main.py)** — routes take a `repo: Repo` parameter and call those
  five methods. No route knows it's talking to SQL, let alone Postgres.

This is the first commit where that seam exists, so there is no earlier
in-memory implementation it was swapped in for — the honest claim is narrower:
introducing the interface and writing the Postgres class against it, in the
same change, is what proves the routes don't need to know the storage
underneath. A second implementation (in-memory, for fast tests; SQLite; a
different database) would be a new class in `repository.py` and nothing else
would move.

## Configuration

Connection details live in `.env` (gitignored — `.env.example` is the
committed template):

```
POSTGRES_USER=taskapi
POSTGRES_PASSWORD=taskapi
POSTGRES_DB=tasks
DATABASE_URL=postgresql://taskapi:taskapi@db:5432/tasks
```

`db` in `DATABASE_URL` is the Postgres service name, resolved inside the
Compose network — not `localhost`. From the host machine (a GUI client, say),
Postgres is reachable at `localhost:5433`; it's mapped there instead of the
default 5432 because that port was already taken by another project on this
machine — see the comment in [docker-compose.yml](docker-compose.yml).

The table is created by [init.sql](init.sql), which Postgres runs
automatically **only the first time the volume is created** — Postgres's own
init-script mechanism, not application code, is what guarantees the three
example tasks are inserted exactly once.

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

{"id":8,"title":"Buy milk","done":false}

$ curl -i http://localhost:8000/tasks/99
HTTP/1.1 404 Not Found
content-length: 29
content-type: application/json

{"error":"Task 99 not found"}

$ curl -i -X PUT http://localhost:8000/tasks/8 -H "Content-Type: application/json" -d '{"done":true}'
HTTP/1.1 200 OK
content-length: 39
content-type: application/json

{"id":8,"title":"Buy milk","done":true}

$ curl -i -X DELETE http://localhost:8000/tasks/8
HTTP/1.1 204 No Content
content-type: application/json

$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{}'
HTTP/1.1 400 Bad Request
content-length: 33
content-type: application/json

{"error":"title: Field required"}
```

(The id is 8, not 1 — Postgres's `SERIAL` keeps counting across every task
ever created on this database, including earlier manual testing; it never
reuses an id.)

## Proof: data survives a full container restart

Not just `docker compose restart` — a full teardown and rebuild, so nothing
about the containers themselves is reused:

```console
$ curl -s http://localhost:8000/tasks/5
{"id":5,"title":"Buy milk","done":false}

$ docker compose down
 Container swaggeruiexplore-app-1  Removed
 Container swaggeruiexplore-db-1  Removed
 Network swaggeruiexplore_default  Removed

$ docker compose up -d
 Container swaggeruiexplore-db-1  Started
 Container swaggeruiexplore-app-1  Started

$ curl -s http://localhost:8000/tasks/5
{"id":5,"title":"Buy milk","done":false}
```

`docker compose down` deletes the containers and the network; it does **not**
touch the `pgdata` named volume (that would need `docker compose down -v`).
The task is still there afterwards because it was never inside the
container — it was in the volume the whole time.

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
