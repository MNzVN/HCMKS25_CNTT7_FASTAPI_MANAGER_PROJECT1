from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.db.database import engine, Base
from app.core.exceptions import AppException, app_exception_handler, generic_exception_handler
import app.models  # Nạp model để tự động tạo bảng
from app.routers import auth

# Tự động tạo bảng DB khi chạy
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Team Project Management API")
app.include_router(auth.router)
# Đăng ký các hàm xử lý lỗi đã viết bên app/core/exceptions.py
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy"}