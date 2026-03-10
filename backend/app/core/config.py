from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OCR Batch Processing System"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./ocr.db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"]

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
