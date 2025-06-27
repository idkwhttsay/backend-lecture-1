from typing import List

from fastapi import APIRouter, HTTPException

from .crud import TaskCRUD
from .models import Task, TaskCreate

router = APIRouter(prefix="/tasks")


@router.post("/create", response_model=Task)
async def create_task(task_data: TaskCreate):
    return TaskCRUD.create_task(task_data)


@router.get("/get_all", response_model=List[Task])
async def get_tasks():
    return TaskCRUD.get_all_tasks()

@router.put("/update/{task_id}", response_model=Task)
async def update_task(task_id: int, task_data: TaskCreate):
    task = TaskCRUD.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/delete/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    task = TaskCRUD.delete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task