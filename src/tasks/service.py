from typing import List, Optional

from sqlmodel import select

from src.auth.models import User
from src.database import SessionDep
from src.tasks.models import Task

class TaskService:
    @staticmethod
    def create_task(task_data, current_user: User, session: SessionDep) -> Task:
        task = Task(**task_data.dict(), completed=False, user_id=current_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_all_tasks(current_user: User, session: SessionDep) -> List[Task]:
        tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
        return list(tasks)

    @staticmethod
    def update_task(task_id: int, task_data, current_user: User, session: SessionDep) -> Optional[Task]:
        task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()

        if task:
            for key, value in task_data.dict().items():
                setattr(task, key, value)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

        return None

    @staticmethod
    def delete_task(task_id: int, current_user: User, session: SessionDep) -> Optional[Task]:
        task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()

        if task:
            session.delete(task)
            session.commit()
            return task

        return None