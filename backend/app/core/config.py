from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import os
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "OCR Batch Processing System"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./ocr.db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v, info):
        if isinstance(v, str) and v:
            return v
        redis_host = info.data.get('REDIS_HOST', 'localhost')
        redis_port = info.data.get('REDIS_PORT', '6379')
        return f"redis://{redis_host}:{redis_port}/0"

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v, info):
        if isinstance(v, str) and v:
            return v
        redis_host = info.data.get('REDIS_HOST', 'localhost')
        redis_port = info.data.get('REDIS_PORT', '6379')
        return f"redis://{redis_host}:{redis_port}/1"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
