from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Xem hồ sơ cá nhân",
    description="Trả về thông tin của user đang đăng nhập.",
    responses={401: {"description": "Thiếu hoặc sai JWT"}},
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Danh sách người dùng",
    description="Tìm kiếm và lọc người dùng.",
    responses={401: {"description": "Thiếu hoặc sai JWT"}, 403: {"description": "Chỉ Admin được truy cập"}},
)
def list_users(
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc email"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return user_service.list_users(search, is_active, db)
