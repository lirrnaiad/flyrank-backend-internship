from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    

tasks = [
    Task(id=1, title="Complete report", done=False),
    Task(id=2, title="Send email", done=False),
    Task(id=3, title="Review code", done=False)
]

current_free_id = 4


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
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


@app.post("/tasks", status_code=201)
def add_task(task: TaskCreate):
    global current_free_id

    if task is None:
        raise HTTPException(status_code=400, detail="Title is empty")

    new_task = Task(id=current_free_id, title=task.title, done=False)
    tasks.append(new_task)
    current_free_id += 1
    return new_task     
