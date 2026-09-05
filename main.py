from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return "Task API is alive"
