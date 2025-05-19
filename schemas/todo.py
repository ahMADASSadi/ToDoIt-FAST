from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from enum import Enum


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.medium

    class Config:
        validate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TaskResponse(TaskBase):
    pk: int = Field(...)
    created_at: datetime
    is_finished: bool


class TaskCreate(TaskBase): ...


class TaskUpdate(TaskBase):
    title: Optional[str] = None  # type: ignore
    description: Optional[str] = None  # type: ignore
    priority: Optional[TaskPriority] = None  # type: ignore
    is_finished: Optional[bool] = None
