from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.enums import ProjectMemberRole
from app.schemas.user import UserResponse

class ProjectBase(BaseModel):
    name: str = Field(...,min_length=1,max_length=255,)
    description: Optional[str] = Field(default=None,max_length=1000,)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)

class ProjectMemberAdd(BaseModel):
    user_id: int
    role: ProjectMemberRole = ProjectMemberRole.MEMBER

class ProjectMemberResponse(BaseModel):
    user_id: int
    role: ProjectMemberRole
    joined_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)