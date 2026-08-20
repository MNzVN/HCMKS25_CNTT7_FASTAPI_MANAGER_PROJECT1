from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import TaskStatus, TaskPriority
from app.schemas.user import UserResponse

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    assignee: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)