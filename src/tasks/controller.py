from typing import Annotated, List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends, Body
from src.auth.service import get_current_active_user

from .service import TaskService
from .models import Task, TaskCreate
from ..auth.models import User
from ..database import SessionDep
from src.tasks.tasks import create_random_task
from src.celery import celery_app

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

@router.post("/random-task", status_code=status.HTTP_201_CREATED)
async def create_random_task(current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep):
    try:
        task_result = create_random_task(current_user, session).delay()

        return {
            "message": "Random task creation triggered successfully",
            "celery_task_id": task_result.id,
            "status": "PENDING"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger task: {str(e)}"
        )

@router.get("/task-status/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_status(
        task_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        task_result = celery_app.AsyncResult(task_id)

        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
            "info": task_result.info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {str(e)}"
        )