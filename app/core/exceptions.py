from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# Bắt lỗi validate dữ liệu đầu vào Pydantic (422)
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


# Bắt lỗi hệ thống chưa xử lý (500)
async def generic_exception_handler(request: Request, exc: Exception):
  return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={
          "success": False,
          "status_code": 500,
          "message": "Đã có lỗi hệ thống xảy ra!",
          "details": {},
      },
  )


