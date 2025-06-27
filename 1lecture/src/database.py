from typing import List

from .tasks.models import Task

_fake_db: List[Task] = []
_id_counter = 1


def save_task(task_data) -> Task:
    global _id_counter
    task = Task(id=_id_counter, completed=False, **task_data.dict())
    _fake_db.append(task)
    _id_counter += 1
    return task


def get_all_tasks() -> List[Task]:
    return _fake_db

def update_task(task_id, task_data):
    for idx, task in enumerate(_fake_db):
        if task.id == task_id:
            updated_task = Task(id=task_id, completed=task.completed, **task_data.dict())
            _fake_db[idx] = updated_task
            return updated_task
    return None

def delete_task(task_id):
    for idx, task in enumerate(_fake_db):
        if task.id == task_id:
            return _fake_db.pop(idx)
    return None
