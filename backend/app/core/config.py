from typing import List
from pydantic import AnyHttpUrl, validator, field_validator
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "OCR Batch Processing System"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./ocr.db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    BACKEND_CORS_ORIGINS: List[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        # 如果环境变量中有 BACKEND_CORS_ORIGINS，使用它
        cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS")
        if cors_origins_env:
            self.BACKEND_CORS_ORIGINS = cors_origins_env.split(",")
        else:
            # 否则使用默认值
            self.BACKEND_CORS_ORIGINS = [
                "http://localhost:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
                "https://ocr-frontend.zeabur.app",
                "https://ocr-web.zeabur.app"
            ]

    @validator("CELERY_BROKER_URL", pre=True)
    def assemble_celery_broker(cls, v: str | None, values: dict[str, any]) -> str:
        if isinstance(v, str) and v:
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/0"

    @validator("CELERY_RESULT_BACKEND", pre=True)
    def assemble_celery_backend(cls, v: str | None, values: dict[str, any]) -> str:
        if isinstance(v, str) and v:
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/1"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

