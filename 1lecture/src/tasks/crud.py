from typing import List, Optional

from src.database import get_all_tasks, save_task, update_task, delete_task, SessionDep
from src.tasks.models import Task, TaskCreate


class TaskCRUD:
    @staticmethod
    def create_task(task_data: TaskCreate, session: SessionDep) -> Task:
        return save_task(task_data, session)

    @staticmethod
    def get_all_tasks(session: SessionDep) -> List[Task]:
        return get_all_tasks(session)

    @staticmethod
    def update_task(task_id: int, task_data: TaskCreate, session: SessionDep) -> Optional[Task]:
        return update_task(task_id, task_data, session)

    @staticmethod
    def delete_task(task_id: int, session: SessionDep) -> Optional[Task]:
        return delete_task(task_id, session)