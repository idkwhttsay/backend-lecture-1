from typing import Annotated, List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends, Body
from src.auth.service import get_current_active_user

from .service import TaskService
from .models import Task, TaskCreate
from ..auth.models import User
from ..database import SessionDep

router = APIRouter(prefix="/tasks")

@router.post("/create", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep):
    return TaskService.create_task(task_data, current_user, session)

@router.get("/get_all", response_model=List[Task], status_code=status.HTTP_200_OK)
async def get_tasks(current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep):
    return TaskService.get_all_tasks(current_user, session)

@router.put("/update/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task_data: Annotated[TaskCreate, Body()], current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep):
    task = TaskService.update_task(task_id, task_data, current_user, session)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.delete("/delete/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep):
    task = TaskService.delete_task(task_id, current_user, session)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
