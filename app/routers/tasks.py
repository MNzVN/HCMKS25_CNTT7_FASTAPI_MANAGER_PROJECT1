from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import tasks as task_service

router = APIRouter(tags=["Tasks"])


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo task",
    description="Tạo task trong project; assignee phải thuộc project.",
    responses={403: {"description": "Không có quyền truy cập project"}, 404: {"description": "Không tìm thấy project"}},
)
def create_task(project_id: int, task_in: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    return task_service.create_task(
        project_id,
        task_in,
        current_user,
        db,
    )

@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[TaskResponse],
    summary="Danh sách task",
    description="Lọc, tìm kiếm, phân trang và sắp xếp task theo created_at hoặc due_date.",
    responses={403: {"description": "Không có quyền truy cập project"}, 404: {"description": "Không tìm thấy project"}},
)
def list_tasks(
    project_id: int,
    status_filter: TaskStatus | None = Query(None, alias="status", description="Lọc theo TODO, IN_PROGRESS hoặc DONE."),
    priority_filter: TaskPriority | None = Query(None, alias="priority", description="Lọc theo LOW, MEDIUM hoặc HIGH."),
    assignee_id: int | None = Query(None, description="Lọc theo ID người được giao."),
    search: str | None = Query(None, description="Tìm gần đúng theo tiêu đề task."),
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1."),
    size: int = Query(20, ge=1, le=100, description="Số task mỗi trang, từ 1 đến 100."),
    sort: str = Query("created_at_desc", description="created_at_asc, created_at_desc, due_date_asc hoặc due_date_desc."),
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
        sort=sort,
        current_user=current_user,
        db=db,
    )

@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Chi tiết task",
    description="Lấy thông tin task nếu user thuộc project chứa task.",
    responses={403: {"description": "Không có quyền truy cập"}, 404: {"description": "Không tìm thấy task"}},
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.get_task(
        task_id=task_id,
        current_user=current_user,
        db=db,
    )

@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Cập nhật task",
    description="Owner cập nhật toàn bộ; assignee chỉ được cập nhật status.",
    responses={400: {"description": "Assignee không thuộc project"}, 403: {"description": "Không có quyền cập nhật"}, 404: {"description": "Không tìm thấy task"}},
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.update_task(
        task_id=task_id,
        task_in=task_in,
        current_user=current_user,
        db=db,
    )

@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa task",
    description="Chỉ owner của project được xóa task.",
    responses={403: {"description": "Chỉ owner được xóa task"}, 404: {"description": "Không tìm thấy task"}},
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_service.delete_task(
        task_id=task_id,
        current_user=current_user,
        db=db,
    )