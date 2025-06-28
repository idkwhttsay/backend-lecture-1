from typing import Annotated, Optional, List

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session, select

from .config import settings
from .tasks.models import Task

engine = create_engine(settings.database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def save_task(task_data, session: SessionDep) -> Task:
    task = Task(**task_data.dict(), completed=False)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_all_tasks(session: SessionDep) -> List[Task]:
    tasks = session.exec(select(Task)).all()
    return list(tasks)

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

def delete_task(task_id, session: SessionDep) -> Optional[Task]:
    task = session.get(Task, task_id)

    if task:
        session.delete(task)
        session.commit()
        return task

    return None
