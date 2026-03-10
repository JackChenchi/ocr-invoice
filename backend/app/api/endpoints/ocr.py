from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import models, schemas
from app.schemas import ocr as ocr_schema
from app.api import deps
from app.services.ocr_service import ocr_service
from app.models.ocr import OCRStatus
import shutil
import os
import uuid
import time
from app.core.config import settings

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", response_model=ocr_schema.OCRResultResponse)
def create_upload_file(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...)
) -> Any:
    if file.content_type not in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]:
        pass 

    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path)

    db_obj = models.ocr.OCRResult(
        file_name=file.filename,
        file_size=file_size,
        status=OCRStatus.PROCESSING,
        image_url=file_path
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    try:
        start_time = time.time()
        result = ocr_service.process_image(file_path)
        
        db_obj.ocr_text = result["text"]
        db_obj.confidence = result["confidence"]
        db_obj.process_time = time.time() - start_time
        db_obj.status = OCRStatus.COMPLETED
        db.commit()
        db.refresh(db_obj)
    except Exception as e:
        db_obj.status = OCRStatus.FAILED
        db_obj.error_msg = str(e)
        db.commit()
        db.refresh(db_obj)

    return db_obj

@router.get("/{id}", response_model=ocr_schema.OCRResultResponse)
def read_ocr_result(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    result = db.query(models.ocr.OCRResult).filter(models.ocr.OCRResult.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="OCR result not found")
    return result

@router.get("/", response_model=List[ocr_schema.OCRResultResponse])
def read_ocr_results(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    results = db.query(models.ocr.OCRResult).offset(skip).limit(limit).all()
    return results
