from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
    description="Tạo tài khoản người dùng mới.",
    responses={400: {"description": "Email đã tồn tại"}, 422: {"description": "Dữ liệu không hợp lệ"}},
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(user_in, db)


@router.post(
    "/login",
    response_model=Token,
    summary="Đăng nhập",
    description="Xác thực tài khoản và cấp access token cùng refresh token.",
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(login_data, db)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Cấp lại access token",
    description="Dùng refresh token hợp lệ để cấp access token mới.",
    responses={401: {"description": "Refresh token không hợp lệ hoặc đã hết hạn"}},
)
def refresh_token(refresh_in: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(refresh_in, db)
