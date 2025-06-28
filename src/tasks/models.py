from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    deadline: Optional[datetime] = None
    description: str

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(..., max_length=100)
    deadline: Optional[datetime] = Field(default=None)
    description: str = Field(..., max_length=500)
    completed: bool = Field(default=False)
