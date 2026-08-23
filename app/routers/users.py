# Task 6 & Task 7 - Day 2
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])


# Task 6 - Day 2: Profile (Lấy thông tin cá nhân của user đang đăng nhập)
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


# Task 7 - Day 2: Danh sách user (Chỉ ADMIN, hỗ trợ tìm kiếm và lọc trạng thái)
@router.get("", response_model=List[UserResponse])
def list_users(
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc email"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),  # Yêu cầu role ADMIN
):
    query = db.query(User)

    # Tìm kiếm theo tên hoặc email nếu có truyền param search
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    # Lọc theo trạng thái is_active nếu có truyền param
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()