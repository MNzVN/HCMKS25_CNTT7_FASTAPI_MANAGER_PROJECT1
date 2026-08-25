from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import TaskPriority
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
from app.services import tasks as task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/projects/{project_id}/tasks",response_model=TaskResponse,status_code=status.HTTP_201_CREATED,)
def create_task(project_id: int, task_in: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    return task_service.create_task(
        project_id,
        task_in,
        current_user,
        db,
    )