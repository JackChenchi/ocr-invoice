from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app import models, schemas
from app.schemas import ocr as ocr_schema
from app.api import deps
from app.services.ocr_service import ocr_service
from app.services.image_preprocessor import image_preprocessor
from app.services.invoice_detector import invoice_detector
from app.services.invoice_extractor import invoice_extractor
from app.services.invoice_validator import invoice_validator
from app.services.excel_exporter import excel_exporter
from app.models.ocr import InvoiceStatus
import shutil
import os
import uuid
import time
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp", "application/pdf"]

def process_invoice_image(file_path: str, db_obj: models.ocr.InvoiceResult, db: Session):
    try:
        start_time = time.time()
        
        processed_path = image_preprocessor.preprocess_for_ocr(file_path)
        
        ocr_result = ocr_service.process_image(processed_path)
        raw_text = ocr_result["text"]
        db_obj.raw_ocr_text = raw_text
        
        detection_result = invoice_detector.is_invoice(raw_text)
        db_obj.is_invoice = detection_result["is_invoice"]
        db_obj.invoice_confidence = detection_result["confidence"]
        
        if not detection_result["is_invoice"]:
            table_data = invoice_extractor._parse_bank_table(raw_text)
            if table_data:
                db_obj.transaction_reference = table_data.get("transaction_reference")
                if table_data.get("amount"):
                    amount_match = __import__('re').search(r'([A-Z]{3})\s*([\d,]+\.?\d*)', table_data["amount"])
                    if amount_match:
                        db_obj.currency = amount_match.group(1)
                        db_obj.total_amount = invoice_extractor.parse_amount(amount_match.group(2))
                    else:
                        db_obj.total_amount = invoice_extractor.parse_amount(table_data["amount"])
                elif table_data.get("currency"):
                    db_obj.currency = table_data.get("currency")
            db_obj.status = InvoiceStatus.NOT_INVOICE
            db_obj.error_msg = "上传的图片不是有效票据类型"
            db_obj.process_time = time.time() - start_time
            db.commit()
            db.refresh(db_obj)
            return db_obj
        
        db_obj.invoice_type = detection_result["invoice_type"]
        
        if detection_result["invoice_type"] in ["银行转账凭证", "银行对账单"]:
            bank_info = invoice_extractor.extract_bank_receipt(raw_text)
            
            db_obj.bank_name = bank_info.bank_name
            db_obj.transaction_reference = bank_info.transaction_reference
            db_obj.transaction_date = bank_info.transaction_date
            db_obj.transaction_time = bank_info.transaction_time
            db_obj.transaction_type = bank_info.transaction_type
            db_obj.source_account = bank_info.source_account
            db_obj.source_account_name = bank_info.source_account_name
            db_obj.receiver_account = bank_info.receiver_account
            db_obj.receiver_account_name = bank_info.receiver_account_name
            db_obj.total_amount = bank_info.amount
            db_obj.currency = bank_info.currency
            db_obj.extraction_confidence = bank_info.confidence
        else:
            invoice_info = invoice_extractor.extract(raw_text)
            
            db_obj.invoice_code = invoice_info.invoice_code
            db_obj.invoice_number = invoice_info.invoice_number
            db_obj.invoice_date = invoice_info.invoice_date
            db_obj.buyer_name = invoice_info.buyer_name
            db_obj.buyer_tax_id = invoice_info.buyer_tax_id
            db_obj.seller_name = invoice_info.seller_name
            db_obj.seller_tax_id = invoice_info.seller_tax_id
            db_obj.total_amount = invoice_info.total_amount
            db_obj.tax_amount = invoice_info.tax_amount
            db_obj.amount_without_tax = invoice_info.amount_without_tax
            db_obj.amount_in_words = invoice_info.amount_in_words
            db_obj.check_code = invoice_info.check_code
            db_obj.extraction_confidence = invoice_info.confidence
            
            validation_result = invoice_validator.validate(invoice_info)
            db_obj.validation_score = validation_result.overall_score
            db_obj.validation_errors = validation_result.errors
            db_obj.validation_warnings = validation_result.warnings
        
        db_obj.status = InvoiceStatus.COMPLETED
        db_obj.process_time = time.time() - start_time
        db.commit()
        db.refresh(db_obj)
        
        if processed_path != file_path and os.path.exists(processed_path):
            os.remove(processed_path)
        
        return db_obj
        
    except Exception as e:
        logger.error(f"Invoice processing failed: {str(e)}")
        db_obj.status = InvoiceStatus.FAILED
        db_obj.error_msg = str(e)
        db.commit()
        db.refresh(db_obj)
        return db_obj

@router.post("/upload", response_model=ocr_schema.InvoiceResultResponse)
def upload_invoice(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...)
) -> Any:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型: {file.content_type}"
        )

    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path)

    db_obj = models.ocr.InvoiceResult(
        file_name=file.filename,
        file_size=file_size,
        status=InvoiceStatus.PROCESSING,
        image_url=file_path
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return process_invoice_image(file_path, db_obj, db)

@router.post("/batch-upload", response_model=ocr_schema.BatchUploadResponse)
def batch_upload_invoices(
    *,
    db: Session = Depends(deps.get_db),
    files: List[UploadFile] = File(...)
) -> Any:
    success_count = 0
    failed_count = 0
    results = []
    errors = []
    
    for file in files:
        try:
            if file.content_type not in ALLOWED_TYPES:
                failed_count += 1
                errors.append({
                    "filename": file.filename,
                    "error": f"不支持的文件类型: {file.content_type}"
                })
                continue
            
            file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            
            db_obj = models.ocr.InvoiceResult(
                file_name=file.filename,
                file_size=file_size,
                status=InvoiceStatus.PROCESSING,
                image_url=file_path
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            result = process_invoice_image(file_path, db_obj, db)
            
            if result.status == InvoiceStatus.COMPLETED:
                success_count += 1
            else:
                failed_count += 1
            
            results.append(ocr_schema.InvoiceResultResponse.model_validate(result))
            
        except Exception as e:
            failed_count += 1
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return ocr_schema.BatchUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results,
        errors=errors
    )

@router.get("/", response_model=ocr_schema.InvoiceListResponse)
def list_invoices(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: InvoiceStatus = None,
    is_invoice: bool = None,
) -> Any:
    query = db.query(models.ocr.InvoiceResult)
    
    if status:
        query = query.filter(models.ocr.InvoiceResult.status == status)
    if is_invoice is not None:
        query = query.filter(models.ocr.InvoiceResult.is_invoice == is_invoice)
    
    total = query.count()
    items = query.order_by(models.ocr.InvoiceResult.upload_time.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return ocr_schema.InvoiceListResponse(
        items=[ocr_schema.InvoiceResultResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=ocr_schema.InvoiceResultResponse)
def get_invoice(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    result = db.query(models.ocr.InvoiceResult).filter(models.ocr.InvoiceResult.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="发票记录不存在")
    return result

@router.delete("/batch/all")
def delete_all_invoices(
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    results = db.query(models.ocr.InvoiceResult).all()
    deleted_count = 0
    
    for result in results:
        if result.image_url and os.path.exists(result.image_url):
            try:
                os.remove(result.image_url)
            except Exception as e:
                logger.warning(f"Failed to delete image file: {result.image_url}, error: {e}")
        db.delete(result)
        deleted_count += 1
    
    db.commit()
    return {"message": f"成功删除 {deleted_count} 条记录", "deleted_count": deleted_count}

@router.delete("/{id}")
def delete_invoice(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    result = db.query(models.ocr.InvoiceResult).filter(models.ocr.InvoiceResult.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="发票记录不存在")
    
    if result.image_url and os.path.exists(result.image_url):
        os.remove(result.image_url)
    
    db.delete(result)
    db.commit()
    return {"message": "删除成功"}

@router.post("/export")
def export_invoices(
    *,
    db: Session = Depends(deps.get_db),
    request: ocr_schema.InvoiceExportRequest,
) -> Any:
    if request.export_all:
        invoices = db.query(models.ocr.InvoiceResult).filter(
            models.ocr.InvoiceResult.status.in_([InvoiceStatus.COMPLETED, InvoiceStatus.NOT_INVOICE])
        ).all()
    elif request.invoice_ids:
        invoices = db.query(models.ocr.InvoiceResult).filter(
            models.ocr.InvoiceResult.id.in_(request.invoice_ids)
        ).all()
    else:
        raise HTTPException(status_code=400, detail="请指定要导出的发票ID或选择导出全部")
    
    if not invoices:
        raise HTTPException(status_code=404, detail="没有可导出的数据")
    
    invoice_data = []
    for inv in invoices:
        validation_status = "有效" if (inv.validation_score or 0) >= 0.7 else "需人工核对"
        invoice_data.append({
            "transaction_reference": inv.transaction_reference or "",
            "total_amount": inv.total_amount,
            "currency": inv.currency or "ETB",
            "image_url": inv.image_url or "",
            "validation_status": validation_status,
        })
    
    buffer = excel_exporter.export_to_bytes(invoice_data, image_dir=UPLOAD_DIR)
    
    from urllib.parse import quote
    filename = excel_exporter.generate_filename("data_export")
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )

@router.get("/statistics/summary")
def get_statistics(
    db: Session = Depends(deps.get_db),
) -> Any:
    total = db.query(models.ocr.InvoiceResult).count()
    completed = db.query(models.ocr.InvoiceResult).filter(
        models.ocr.InvoiceResult.status == InvoiceStatus.COMPLETED
    ).count()
    failed = db.query(models.ocr.InvoiceResult).filter(
        models.ocr.InvoiceResult.status == InvoiceStatus.FAILED
    ).count()
    not_invoice = db.query(models.ocr.InvoiceResult).filter(
        models.ocr.InvoiceResult.status == InvoiceStatus.NOT_INVOICE
    ).count()
    
    total_amount = db.query(models.ocr.InvoiceResult).filter(
        models.ocr.InvoiceResult.status == InvoiceStatus.COMPLETED,
        models.ocr.InvoiceResult.is_invoice == True
    ).with_entities(
        models.ocr.InvoiceResult.total_amount
    ).all()
    
    total_amount_sum = sum(row[0] or 0 for row in total_amount)
    total_tax_sum = sum(
        row[0] or 0 
        for row in db.query(models.ocr.InvoiceResult.tax_amount).filter(
            models.ocr.InvoiceResult.status == InvoiceStatus.COMPLETED,
            models.ocr.InvoiceResult.is_invoice == True
        ).all()
    )
    
    return {
        "total_count": total,
        "completed_count": completed,
        "failed_count": failed,
        "not_invoice_count": not_invoice,
        "total_amount": total_amount_sum,
        "total_tax": total_tax_sum,
    }
