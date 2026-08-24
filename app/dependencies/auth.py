import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User

# Khai báo schema đọc Bearer Token từ Header "Authorization: Bearer <token>"
security_scheme = HTTPBearer()

# Task 4-day2: Dependency giải mã token và lấy User hiện tại
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme),db: Session = Depends(get_db),) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã JWT token bằng SECRET_KEY
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Lấy user_id được lưu trong trường "sub" của token
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        # Chuyển user_id từ chuỗi sang số nguyên để truy vấn database
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    # Tìm user trong DB
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Kiểm tra trạng thái tài khoản
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa",
        )
    return user

# Task 5-day2: Dependency kiểm tra quyền Admin
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền quản trị viên (Admin)",
        )
    return current_user