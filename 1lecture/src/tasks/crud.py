from typing import List, Optional

from src.database import get_all_tasks, save_task, update_task, delete_task
from src.tasks.models import Task, TaskCreate


class TaskCRUD:
    @staticmethod
    def create_task(task_data: TaskCreate) -> Task:
        return save_task(task_data)

    @staticmethod
    def get_all_tasks() -> List[Task]:
        return get_all_tasks()

    @staticmethod
    def update_task(task_id: int, task_data: TaskCreate) -> Optional[Task]:
        return update_task(task_id, task_data)

    @staticmethod
    def delete_task(task_id: int) -> Optional[Task]:
        return delete_task(task_id)