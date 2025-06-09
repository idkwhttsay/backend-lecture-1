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
