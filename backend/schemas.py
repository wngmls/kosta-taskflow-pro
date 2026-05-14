from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from models import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    due_at: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_at: Optional[datetime] = None


class TaskListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TaskStatus
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TaskResponse(TaskListResponse):
    description: Optional[str]
