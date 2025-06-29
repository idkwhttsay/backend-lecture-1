from typing import List, Optional

from sqlmodel import select

from src.database import SessionDep
from src.tasks.models import Task


class TaskService:
    @staticmethod
    def create_task(task_data, session: SessionDep) -> Task:
        task = Task(**task_data.dict(), completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_all_tasks(session: SessionDep) -> List[Task]:
        tasks = session.exec(select(Task)).all()
        return list(tasks)

    @staticmethod
    def update_task(task_id: int, task_data, session: SessionDep) -> Optional[Task]:
        task = session.get(Task, task_id)

        if task:
            for key, value in task_data.dict().items():
                setattr(task, key, value)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

        return None

    @staticmethod
    def delete_task(task_id: int, session: SessionDep) -> Optional[Task]:
        task = session.get(Task, task_id)

        if task:
            session.delete(task)
            session.commit()
            return task

        return None