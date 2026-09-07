import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DB_FILE = "tasks.db"


# Database
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT 0
        )
    """)

    # Seed 3 tasks
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Walk the dog", 1),
                ("Wash clothes", 0),
                ("Do today's reports", 0),
            ],
        )
    conn.commit()
    conn.close()


# Pydantic Models
class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# App
app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.1", "endpoints": ["/tasks"]}


@app.get("/health", description="Check if system is running.")
def check_health():
    return {"status": "ok"}


@app.get("/tasks", description="Returns every task in the system.")
def get_tasks():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    conn.close()
    return [dict(r) | {"done": bool(r["done"])} for r in rows]


@app.get("/tasks/{task_id}", description="Retrieve a single task by its ID.")
def get_task(task_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(404, "Task not found")
    return dict(row) | {"done": bool(row["done"])}


@app.post("/tasks", status_code=201, description="Add a new task.")
def add_task(task: TaskCreate):
    if task is None or (task.title == "" or task.title is None):
        raise HTTPException(status_code=400, detail="Title is empty")

    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )
    
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row) | {"done": bool(row["done"])}
