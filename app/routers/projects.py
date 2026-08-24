from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED,)
def create_project(project_in: ProjectCreate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)
 
    return project

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    search: Optional[str] = Query(None, description="Tìm theo tên dự án"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Project)
        .outerjoin(ProjectMember, Project.id == ProjectMember.project_id)
        .filter(
            or_(
                Project.owner_id == current_user.id,
                ProjectMember.user_id == current_user.id,
            )
        )
    )

    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    return query.distinct().all()