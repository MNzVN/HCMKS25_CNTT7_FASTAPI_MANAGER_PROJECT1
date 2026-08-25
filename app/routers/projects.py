from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import projects as project_service

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED,)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.create_project(project_in, current_user, db)


@router.get("", response_model=List[ProjectResponse])
def list_projects(search: Optional[str] = Query(None, description="Tìm theo tên dự án"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    return project_service.list_projects(search, current_user, db)

@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_detail(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    return project_service.get_project_detail(project_id, current_user, db)

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.update_project(project_id, project_in, current_user, db)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_service.delete_project(project_id, current_user, db)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED,)
def add_project_member(project_id: int, member_in: ProjectMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.add_project_member(project_id, member_in, current_user, db)

@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_service.remove_project_member(project_id, user_id, current_user, db)

@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def list_project_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.list_project_members(project_id, current_user, db)
