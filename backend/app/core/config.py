from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import os
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "神眼系统"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./ocr.db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    BACKEND_CORS_ORIGINS: List[str] = []
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    OCR_LANGS: str = "ch,en"
    OCR_CONFIDENCE_THRESHOLD: float = 0.6
    OCR_RETRY_ENABLED: bool = True
    OCR_RETRY_MIN_GAIN: float = 0.03
    OCR_USE_MKLDNN: bool = False
    OCR_USE_GPU: bool = False
    OCR_USE_ANGLE_CLS: bool = False
    OCR_OMP_NUM_THREADS: int = 1
    DATA_RETENTION_DAYS: int = 365
    IMAGE_RETENTION_DAYS: int = 180

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                try:
                    data = json.loads(v)
                    if isinstance(data, list):
                        return data
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
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
