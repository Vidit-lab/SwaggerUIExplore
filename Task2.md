A1 — Connecting your CRUD to the database

💡 New words are marked in bold the first time they appear. Every bold word is explained in the Glossary at the bottom.
Goal

Take the CRUD API you built in Assignment 1 and replace the in-memory task list with a real SQLite database. Your API endpoints should continue to behave exactly the same, but now your data survives when the server restarts.
Purpose

Last assignment, your tasks disappeared every time you restarted the server. That wasn't a bug, it was the limitation of storing data in memory.

Real applications store their data in databases. Instead of keeping a list of tasks inside your code, your server will now save them in SQLite, a lightweight database stored in a single file on your computer.

The exciting part is that almost none of your API changes. Clients still send the same requests to the same endpoints. Only the storage layer changes.

This is one of the biggest ideas in backend development:

APIs describe what your application does. Databases describe where your application stores its data.
The big idea in 60 seconds

So far your architecture looked like this:

Client -> API -> Array in memory

Now it becomes:

Client -> API -> SQL Database

The client doesn't know the difference.

GET /tasks still returns tasks.

POST /tasksstill creates tasks.

PUT still updates.

DELETE still deletes.

The only difference is that restarting your server no longer deletes everything.

🐍 Python lane

    Database: SQL Lite
    Library: SQLModel or sqlite3
    Database file: tasks.db

SQLite requires no installation or server.

The first time your application runs, it will automatically create the database file.
The task — six stages
Stage 0 — Create your database (~30 min)

Instead of creating an array of tasks, create a SQLite database called:

tasks.db

Create a table named:

tasks

with these columns:

    id (integer primary key)
    title (text)
    done (boolean)

When your application starts:

    create the table if it doesn't already exist
    insert three example tasks only if the table is empty

Checkpoint:

Restart your application several times.

The example tasks should only appear once.

Commit:

Stage 0: create SQLite database
Stage 1 — Read from the database (~45 min)

Replace the code that reads from your in-memory array.

GET /tasks should now execute a SQL query that returns every task.

GET /tasks/{id} should return one task from the database.

Unknown ids still return:

404{ "error": "Task not found"}

Nothing about your API should change.

Checkpoint:

GET /tasks

returns the database contents.

Commit:

Stage 1: database read endpoints
Stage 2 — Create new tasks (~45 min)

POST /tasks should now insert a new row into the database instead of pushing into an array.

The same validation rules still apply.

Missing title:

400

Successful request:

201

Checkpoint:

Create several tasks.

Restart the server.

Run GET /tasks again.

The tasks should still exist.

This is the first time your data survives a restart.

Commit:

Stage 2: insert into database
Stage 3 — Update and delete (~45 min)

Replace your update and delete logic with SQL.

PUT should update a row.

DELETE should remove a row.

The API behaviour should remain identical.

Checkpoint:

Create a task.

Update it.

Delete it.

Confirm every operation using GET /tasks.

Commit:

Stage 3: update and delete with SQL
Stage 4 — Learn your first SQL (~45 min)

Open the database using any SQLite viewer (DB Browser for SQLite is recommended).

Run these queries manually:

List every task:

SELECT * FROM tasks;

Show only completed tasks:

SELECT * FROM tasks WHERE done = 1;

Count all tasks:

SELECT COUNT(*) FROM tasks;

Mark every task as completed:

UPDATE tasks SET done = 1;

Delete all completed tasks:

DELETE FROM tasks WHERE done = 1;

Notice how the API immediately reflects your database changes.

Checkpoint:

Modify the database manually and verify the changes through your API.

Commit:

Stage 4: explored SQLite
Stage 5 — Publish your database project (~30 min)

Update your README.

Add:

    why SQLite was chosen
    where the database file is stored
    how to start the project
    a screenshot of your database viewer
    one example SQL query you executed

Checkpoint:

Someone cloning your repository can run the project and automatically create the database.

Commit:

Stage 5: database documentation