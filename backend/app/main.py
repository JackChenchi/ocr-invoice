from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import ocr, invoice
from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.on_event("startup")
async def startup_event():
    logger.info("Preloading OCR model...")
    try:
        from app.services.ocr_service import _get_ocr_instance
        _get_ocr_instance()
        logger.info("OCR model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load OCR model: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

upload_dir = "uploads"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(invoice.router, prefix="/invoice", tags=["invoice"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Invoice OCR System"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
