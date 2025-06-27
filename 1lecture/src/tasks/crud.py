from typing import List, Optional
from sqlalchemy.orm import Session

from src.database import TaskDB
from src.tasks.models import Task, TaskCreate


class TaskCRUD:
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> Task:
        db_task = TaskDB(**task_data.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_all_tasks(db: Session) -> List[Task]:
        tasks = db.query(TaskDB).all()
        return tasks

    @staticmethod
    def update_task(db: Session, task_id: int, task_data: TaskCreate) -> Optional[Task]:
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if db_task:
            for key, value in task_data.dict().items():
                setattr(db_task, key, value)
            db.commit()
            db.refresh(db_task)
            return db_task
        return None

    @staticmethod
    def delete_task(db: Session, task_id: int) -> Optional[Task]:
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if db_task:
            db.delete(db_task)
            db.commit()
            return db_task
        return None