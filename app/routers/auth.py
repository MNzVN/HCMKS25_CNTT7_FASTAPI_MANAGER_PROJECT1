from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED,)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(user_in, db)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(login_data, db)
