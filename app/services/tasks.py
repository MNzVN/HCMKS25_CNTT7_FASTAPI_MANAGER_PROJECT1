from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import ProjectMember
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.enums import TaskPriority, TaskStatus
from app.services.projects import (
    get_project_or_404,
    require_owner,
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

def list_tasks(
    project_id: int,
    status_filter: TaskStatus | None,
    priority_filter: TaskPriority | None,
    assignee_id: int | None,
    search: str | None,
    page: int,
    size: int,
    sort: str,
    current_user,
    db: Session,
) -> list[Task]:
    project = get_project_or_404(project_id, db)
    require_access(project, current_user, db)

    query = db.query(Task).filter(Task.project_id == project_id)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter)

    if priority_filter is not None:
        query = query.filter(Task.priority == priority_filter)

    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)

    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    if sort == "created_at_asc":
        query = query.order_by(Task.created_at.asc())
    elif sort == "due_date_asc":
        query = query.order_by(Task.due_date.asc())
    elif sort == "due_date_desc":
        query = query.order_by(Task.due_date.desc())
    else:
        query = query.order_by(Task.created_at.desc())

    offset = (page - 1) * size

    return (
        query
        .offset(offset)
        .limit(size)
        .all()
    )

def get_task(task_id: int, current_user, db: Session,) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy task",
        )

    project = get_project_or_404(task.project_id, db)
    require_access(project, current_user, db)

    return task

def require_update_permission(task: Task, current_user) -> None:
    if task.project.owner_id == current_user.id:
        return

    if task.assignee_id == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Bạn không có quyền cập nhật task này",
    )

def update_task(task_id: int, task_in: TaskUpdate, current_user, db: Session,) -> Task:
    task = get_task(task_id, current_user, db)
    project = get_project_or_404(task.project_id, db)
    require_update_permission(task, current_user)

    update_data = task_in.model_dump(exclude_unset=True)

    if project.owner_id != current_user.id:
        if set(update_data) - {"status"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assignee chỉ được cập nhật trạng thái task",
            )

    if task_in.assignee_id is not None:
        assignee_is_owner = project.owner_id == task_in.assignee_id

        assignee_is_member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project.id,
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

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task

def delete_task(task_id: int,current_user,db: Session,) -> None:
    task = get_task(task_id, current_user, db)
    project = get_project_or_404(task.project_id, db)
    require_owner(project, current_user)

    db.delete(task)
    db.commit()