from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Cấu hình Database ---
    # Đọc từ biến môi trường DATABASE_URL trong file .env
    DATABASE_URL: str

    # --- Cấu hình JWT ---
    # Đọc từ biến môi trường SECRET_KEY trong file .env
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()