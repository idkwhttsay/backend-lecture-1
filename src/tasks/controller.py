from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Body, status

from .service import TaskService
from .models import Task, TaskCreate
from ..database import SessionDep

router = APIRouter(prefix="/tasks")

@router.post("/create", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, session: SessionDep):
    return TaskService.create_task(task_data, session)

@router.get("/get_all", response_model=List[Task], status_code=status.HTTP_200_OK)
async def get_tasks(session: SessionDep):
    return TaskService.get_all_tasks(session)

@router.put("/update/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task_data: Annotated[TaskCreate, Body()], session: SessionDep):
    task = TaskService.update_task(task_id, task_data, session)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.delete("/delete/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, session: SessionDep):
    task = TaskService.delete_task(task_id, session)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task