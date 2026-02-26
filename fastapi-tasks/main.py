from fastapi import FastAPI
from pydantic import BaseModel
import json
import os

app = FastAPI()

TASKS_FILE = "tasks.txt"


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool = False


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


def load_tasks():
    tasks = []

    if not os.path.exists(TASKS_FILE):
        return tasks

    f = open(TASKS_FILE, "r", encoding="utf-8")
    for line in f:
        line = line.strip()
        if line != "":
            tasks.append(json.loads(line))
    f.close()

    return tasks


def save_tasks(tasks):
    f = open(TASKS_FILE, "w", encoding="utf-8")
    for task in tasks:
        f.write(json.dumps(task) + "\n")
    f.close()


def get_next_id(tasks):
    if len(tasks) == 0:
        return 1

    biggest = tasks[0]["id"]
    for t in tasks:
        if t["id"] > biggest:
            biggest = t["id"]

    return biggest + 1


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/tasks")
def get_tasks(completed: bool | None = None):
    tasks = load_tasks()

    if completed is None:
        return tasks

    filtered = []
    for t in tasks:
        if t["completed"] == completed:
            filtered.append(t)

    return filtered

@app.get("/tasks/stats")
def task_stats():
    tasks = load_tasks()

    total = len(tasks)
    completed = 0

    for t in tasks:
        if t["completed"] == True:
            completed += 1

    pending = total - completed

    if total == 0:
        percent = 0
    else:
        percent = (completed / total) * 100

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_percentage": percent
    }

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    tasks = load_tasks()

    for t in tasks:
        if t["id"] == task_id:
            return t

    return {"message": "Task not found"}


@app.post("/tasks")
def create_task(new_task: TaskCreate):
    tasks = load_tasks()

    task = {
        "id": get_next_id(tasks),
        "title": new_task.title,
        "description": new_task.description,
        "completed": new_task.completed
    }

    tasks.append(task)
    save_tasks(tasks)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: Task):
    tasks = load_tasks()

    for i in range(len(tasks)):
        if tasks[i]["id"] == task_id:
            task_dict = updated.model_dump()
            task_dict["id"] = task_id
            tasks[i] = task_dict
            save_tasks(tasks)
            return {"message": "Task updated", "task": task_dict}

    return {"message": "Task not found"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    new_list = []
    found = False

    for t in tasks:
        if t["id"] == task_id:
            found = True
        else:
            new_list.append(t)

    if found:
        save_tasks(new_list)
        return {"message": "Task deleted"}
    else:
        return {"message": "Task not found"}


@app.delete("/tasks")
def delete_all_tasks():
    save_tasks([])
    return {"message": "All tasks deleted"}


