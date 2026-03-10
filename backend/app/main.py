from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import ocr, invoice
from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine
import os

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

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
