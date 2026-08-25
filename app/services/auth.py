from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate


def register_user(user_in: UserCreate, db: Session) -> User:
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng",
        )

    new_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.USER,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(login_data: LoginRequest, db: Session) -> dict[str, str]:
    user = db.query(User).filter(User.email == login_data.email).first()
    if user is None or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}
