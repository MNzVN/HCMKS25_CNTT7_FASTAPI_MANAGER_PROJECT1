from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
from app.services import tasks as task_service

router = APIRouter(tags=["Tasks"])


@router.post("/projects/{project_id}/tasks",response_model=TaskResponse,status_code=status.HTTP_201_CREATED,)
def create_task(project_id: int, task_in: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    return task_service.create_task(
        project_id,
        task_in,
        current_user,
        db,
    )

@router.get("/projects/{project_id}/tasks",response_model=list[TaskResponse],)
def list_tasks(
    project_id: int,
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority_filter: TaskPriority | None = Query(None, alias="priority"),
    assignee_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.list_tasks(
        project_id=project_id,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assignee_id=assignee_id,
        search=search,
        page=page,
        size=size,
        current_user=current_user,
        db=db,
    )