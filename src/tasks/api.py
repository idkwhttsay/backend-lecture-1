from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Body, status

from src.database import get_db
from .crud import TaskCRUD
from .models import Task, TaskCreate
from ..database import SessionDep

router = APIRouter(prefix="/tasks")

@router.post("/create", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, session: SessionDep):
    return TaskCRUD.create_task(task_data, session)

@router.get("/get_all", response_model=List[Task], status_code=status.HTTP_200_OK)
async def get_tasks(session: SessionDep):
    return TaskCRUD.get_all_tasks(session)

@router.put("/update/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task_data: Annotated[TaskCreate, Body()], session: SessionDep):
    task = TaskCRUD.update_task(task_id, task_data, session)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.delete("/delete/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, session: SessionDep):
    task = TaskCRUD.delete_task(task_id, session)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task