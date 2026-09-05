-- Runs once, only when the Postgres data volume is first created.
CREATE TABLE IF NOT EXISTS tasks (
    id    SERIAL PRIMARY KEY,
    title TEXT    NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, done) VALUES
    ('Read the FastAPI docs', TRUE),
    ('Build a CRUD API', FALSE),
    ('Push it to GitHub', FALSE);
