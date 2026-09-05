W2 · A1 — Build your first CRUD API

💡 New words are marked in bold the first time they appear. Every bold word is explained in the Glossary at the bottom. If a sentence confuses you, check the glossary first — it's probably one word, not the whole idea.
Goal

Build a small API that manages a to-do list: you can create tasks, read them, update them, and delete them — the four CRUD operations. You will see and test your API in a visual page called Swagger UI, and publish everything to GitHub.
Purpose

In the lecture you watched the request → response loop from the outside. Now you build the server side of it yourself. CRUD is the heartbeat of almost every backend in the world — a social network CRUDs posts, a shop CRUDs orders, FlyRank CRUDs SEO reports. Once you've built CRUD once, every backend you ever meet will feel familiar.

Two habits start here: your data lives only in memory (no database yet — that's next week, and losing your data on restart is a lesson, not a bug), and everything is submitted through GitHub (that's how all work in this program is shared).

Beginners usually overthink this. The whole thing is under 100 lines of code, built in small stages. You never write more than ~15 lines before you can test again.
The big idea in 60 seconds

Your API is a server — a program that waits for requests and sends back responses. It offers several endpoints. An endpoint is one "door" into your server, defined by two things:

    a path — where the door is, like /tasks or /tasks/3

    an HTTP method — what kind of knock it answers to: GET (give me), POST (create this), PUT (replace this), DELETE (remove this)

So GET /tasks ("give me all tasks") and POST /tasks ("create a task") are two different endpoints, even though the path is the same. The four CRUD operations map onto the methods like this:
CRUD operation	HTTP method	Example endpoint	Meaning
Create	POST	POST /tasks	Add a new task
Read	GET	GET /tasks · GET /tasks/3	List all tasks / get task 3
Update	PUT	PUT /tasks/3	Change task 3
Delete	DELETE	DELETE /tasks/3	Remove task 3

That table is the assignment. Everything below just builds it, one row at a time.
Tools — pick ONE lane

Both lanes build exactly the same API. Pick the language you want to stick with; don't switch mid-assignment.
	🟨 JavaScript lane	🐍 Python lane
Language	Node.js (free, nodejs.org (opens in a new tab))	Python 3.10+ (free, python.org (opens in a new tab))
Framework	Express — Hello world (opens in a new tab)	FastAPI — First steps (opens in a new tab)
Swagger UI	Add with swagger-ui-express (opens in a new tab) (Stage 5)	Built in at /docs — zero setup
Testing your API	curl + browser + Hoppscotch (opens in a new tab) (all free)	same
Publishing	Git + a free GitHub (opens in a new tab) account	same

Not sure? If you liked the JS 101 session, take the JavaScript lane. If Python feels friendlier, take the Python lane — you'll get Swagger for free, which is a nice reward.
The task — six stages (+ one bonus)

Work stage by stage, in order. Each stage ends with a checkpoint: a command you run to prove it works. Commit to Git after every stage (that's your ≥6 commits, honestly earned). If you only finish Stage 3, submit anyway — a working half is worth more than a broken whole.
Stage 0 — Hello, server (~30 min)

The scene: before a restaurant serves food, the doors have to open.

    Install your lane's tools (Node or Python — see the W2 resources, section 6).

    Follow your framework's official hello-world page (linked in the table above) to start a server on localhost — Express on port 3000, FastAPI on port 8000.

    Visit it in your browser. You should see your hello message.

Checkpoint: curl -i http://localhost:3000/ (or :8000/) returns status code 200 and your message.

Commit: Stage 0: hello server
Stage 1 — Your first real endpoint (~45 min)

Every API needs a front door that says what it is.

    Add the endpoint GET / returning JSON that describes your API:

{ "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

    Add GET /health returning { "status": "ok" } . Real companies use exactly this endpoint to check a server is alive — you've just built your first professional habit.

Checkpoint: both URLs return JSON in the browser and via curl.

Commit: Stage 1: root and health endpoints
Stage 2 — Read: list and single task (~1 h)

Now the shelves. Your "database" is just a list in your code.

    Near the top of your file, create an in-memory list of task objects, pre-filled with 3 example tasks. Each task has: id (number), title (text), done (true/false).

    Add GET /tasks — returns the whole list.

    Add GET /tasks/:id (Express) / GET /tasks/{id} (FastAPI) — returns one task. The id part is a path parameter : a piece of the URL that changes.

    If no task has that id, return status 404 with a JSON error: { "error": "Task 99 not found" } . Never return an empty 200 for something that doesn't exist — status codes are how machines read your answers.

Checkpoint: curl -i http://localhost:3000/tasks/1 → 200 + one task · curl -i http://localhost:3000/tasks/99 → 404 + error JSON.

Commit: Stage 2: read endpoints with 404
Stage 3 — Create: POST a new task (~1 h)

A customer walks in with a new order.

    Add POST /tasks . The client sends the new task as JSON in the request body :

{ "title": "Buy milk" }

    Your server: gives it the next free id , sets done to false , adds it to the list, and returns the created task with status 201 ("Created" — the polite way to say "done, here's your receipt").

    Validate the input: if title is missing or empty, return 400 ("Bad Request") with a JSON error saying what's wrong. This is your first business rule — the server never trusts the client.

Checkpoint:

curl -i -X POST [http://localhost:3000/tasks](http://localhost:3000/tasks) -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

returns 201 + the new task, and a second GET /tasks shows it in the list. Posting {} returns 400.

Commit: Stage 3: create with validation
Stage 4 — Update & Delete (~1 h)

Orders change, orders get cancelled.

    Add PUT /tasks/:id — replaces a task's title and/or done with what's in the request body. Returns the updated task. Unknown id → 404 . Empty/invalid body → 400 .

    Add DELETE /tasks/:id — removes the task. Return status 204 ("No Content" — success, nothing to say) with an empty body. Unknown id → 404 .

    🎉 Stop and notice: you have built a complete CRUD API. Every backend you'll ever work on is this, wearing more clothes.

Checkpoint: create a task, update it, mark it done, delete it, and confirm with GET /tasks — all via curl, all with the right status codes (201, 200, 204, 404).

Commit: Stage 4: full CRUD
Stage 5 — See it: Swagger UI (~1–1.5 h)

So far you've imagined your API. Now look at it.

Swagger UI is a web page that reads a description of your API (an OpenAPI file) and turns it into interactive documentation: every endpoint listed, with a Try it out button that sends real requests — curl with a friendly face.

    🐍 Python lane: open http://localhost:8000/docs . It's already there — FastAPI generates it from your code. Add a one-line description to each endpoint (see First steps (opens in a new tab) ) and watch the page improve.

    🟨 JavaScript lane: install swagger-ui-express , write a small openapi.json describing your five task endpoints (the package README (opens in a new tab) shows the wiring; OpenAPI basic structure (opens in a new tab) explains the file). Serve it at /docs . Describing endpoints you already built teaches you more than building them did.

Then, in Swagger UI, without curl: create a task, list tasks, update it, delete it.

Checkpoint: /docs shows all your endpoints; "Try it out" works for the full CRUD cycle. Take a screenshot for your README.

Commit: Stage 5: Swagger UI
Stage 6 — Publish to GitHub (~1 h)

Your work only counts when someone else can run it.

    Create a public GitHub repo and push your code (your ≥6 stage commits come with it).

    Write a README with: what this is, how to install & run it (one documented command), a table of all endpoints, one pasted curl -i output, and your Swagger screenshot.

Checkpoint: a stranger with your README could run your API in under 5 minutes.

Commit: Stage 6: publish and docs — then push everything.

Requirements

Done = every box ticked. Each one is checkable in under a minute.

    Server starts with one documented command on localhost.

    GET /tasks , GET /tasks/:id , POST /tasks , PUT /tasks/:id , DELETE /tasks/:id all work — full CRUD on an in-memory list (no database, no files).

    Correct status codes: 200 reads, 201 create, 204 delete, 400 invalid body, 404 unknown id — each error with a JSON error message.

    POST and PUT validate input (missing/empty title → 400 ).

    Swagger UI at /docs lists every endpoint, and the full CRUD cycle works via "Try it out".

    Public GitHub repo , ≥6 meaningful commits (one per stage), README with run instructions, endpoint table, one curl -i output, and the Swagger screenshot.
