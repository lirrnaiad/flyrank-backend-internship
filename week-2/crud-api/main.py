from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


tasks = [
    Task(id=1, title="Complete report", done=False),
    Task(id=2, title="Send email", done=False),
    Task(id=3, title="Review code", done=False)
]


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def status():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task_index = task_id - 1

    try:
        task = tasks[task_index]
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    else:
        return task
