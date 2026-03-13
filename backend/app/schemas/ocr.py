from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.ocr import OCRStatus, InvoiceStatus

class OCRResultBase(BaseModel):
    file_name: str
    file_size: int

class OCRResultCreate(OCRResultBase):
    pass

class OCRResultUpdate(OCRResultBase):
    status: OCRStatus
    ocr_text: Optional[str] = None
    confidence: Optional[float] = None
    process_time: Optional[float] = None
    error_msg: Optional[str] = None

class OCRResultResponse(OCRResultBase):
    id: int
    upload_time: datetime
    status: OCRStatus
    ocr_text: Optional[str] = None
    confidence: Optional[float] = None
    process_time: Optional[float] = None
    error_msg: Optional[str] = None
    coordinates: Optional[Any] = None

    class Config:
        from_attributes = True

class InvoiceResultBase(BaseModel):
    file_name: str
    file_size: int

class InvoiceResultCreate(InvoiceResultBase):
    pass

class InvoiceResultResponse(InvoiceResultBase):
    id: int
    upload_time: datetime
    process_time: Optional[float] = None
    status: InvoiceStatus
    error_msg: Optional[str] = None
    image_url: Optional[str] = None
    
    invoice_code: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    invoice_type: Optional[str] = None
    
    buyer_name: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_bank: Optional[str] = None
    buyer_account: Optional[str] = None
    
    seller_name: Optional[str] = None
    seller_tax_id: Optional[str] = None
    seller_address: Optional[str] = None
    seller_phone: Optional[str] = None
    seller_bank: Optional[str] = None
    seller_account: Optional[str] = None
    
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    amount_without_tax: Optional[float] = None
    amount_in_words: Optional[str] = None
    
    check_code: Optional[str] = None
    currency: Optional[str] = "CNY"
    remarks: Optional[str] = None
    
    transaction_reference: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_time: Optional[str] = None
    receiver_account: Optional[str] = None
    receiver_account_name: Optional[str] = None
    
    is_invoice: bool = True
    invoice_confidence: float = 0.0
    extraction_confidence: float = 0.0
    validation_score: float = 0.0
    validation_errors: Optional[List[str]] = None
    validation_warnings: Optional[List[str]] = None
    needs_review: Optional[bool] = None

    class Config:
        from_attributes = True

class InvoiceListResponse(BaseModel):
    items: List[InvoiceResultResponse]
    total: int
    page: int
    page_size: int

class InvoiceExportRequest(BaseModel):
    invoice_ids: Optional[List[int]] = None
    export_all: bool = False
    fields: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    include_images: bool = False

class BatchUploadResponse(BaseModel):
    success_count: int
    failed_count: int
    results: List[InvoiceResultResponse]
    errors: List[dict] = []
