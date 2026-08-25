from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import ProjectMember
from app.models.task import Task
from app.schemas.task import TaskCreate
from app.services.projects import (
    get_project_or_404,
    require_access,
)


def create_task(project_id: int, task_in: TaskCreate, current_user, db: Session,) -> Task:
    project = get_project_or_404(project_id, db)
    require_access(project, current_user, db)

    if task_in.assignee_id is not None:
        assignee_is_owner = project.owner_id == task_in.assignee_id

        assignee_is_member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == task_in.assignee_id,
            )
            .first()
            is not None
        )

        if not assignee_is_owner and not assignee_is_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao phải là thành viên của dự án",
            )

    task = Task(
        project_id=project_id,
        title=task_in.title,
        description=task_in.description,
        assignee_id=task_in.assignee_id,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task