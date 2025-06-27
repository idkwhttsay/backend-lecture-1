from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from .crud import TaskCRUD
from .models import Task, TaskCreate

router = APIRouter(prefix="/tasks")


@router.post("/create", response_model=Task)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    return TaskCRUD.create_task(db, task_data)


@router.get("/get_all", response_model=List[Task])
async def get_tasks(db: Session = Depends(get_db)):
    return TaskCRUD.get_all_tasks(db)


@router.put("/update/{task_id}", response_model=Task)
async def update_task(task_id: int, task_data: TaskCreate, db: Session = Depends(get_db)):
    task = TaskCRUD.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/delete/{task_id}", response_model=Task)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = TaskCRUD.delete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task