from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(HTTPException):

  def __init__(self, status_code: int, message: str, details: dict = None):
    super().__init__(status_code=status_code, detail=message)
    self.message = message
    self.details = details or {}


# 1. Bắt custom AppException nghiệp vụ (400, 401, 403, 404,...)
async def app_exception_handler(request: Request, exc: AppException):
  return JSONResponse(
      status_code=exc.status_code,
      content={
          "success": False,
          "status_code": exc.status_code,
          "message": exc.message,
          "details": exc.details,
      },
  )


# 2. Bắt lỗi validate dữ liệu đầu vào Pydantic (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
  return JSONResponse(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      content={
          "success": False,
          "status_code": 422,
          "message": "Dữ liệu gửi lên không hợp lệ",
          "details": exc.errors(),
      },
  )


# 3. Bắt lỗi hệ thống chưa xử lý (500)
async def generic_exception_handler(request: Request, exc: Exception):
  return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={
          "success": False,
          "status_code": 500,
          "message": "Đã có lỗi hệ thống xảy ra!",
          "details": str(exc),
      },
  )


