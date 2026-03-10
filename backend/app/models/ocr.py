from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Enum, Boolean
from sqlalchemy.sql import func
import enum
from app.db.base_class import Base

class OCRStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_INVOICE = "not_invoice"

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, server_default=func.now(), nullable=False)
    ocr_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    process_time = Column(Float, nullable=True)
    status = Column(Enum(OCRStatus), default=OCRStatus.PENDING, nullable=False)
    error_msg = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    coordinates = Column(JSON, nullable=True)

class InvoiceResult(Base):
    __tablename__ = "invoice_results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, server_default=func.now(), nullable=False)
    process_time = Column(Float, nullable=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False)
    error_msg = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    
    invoice_code = Column(String(20), nullable=True)
    invoice_number = Column(String(20), nullable=True)
    invoice_date = Column(String(20), nullable=True)
    invoice_type = Column(String(50), nullable=True)
    
    buyer_name = Column(String(200), nullable=True)
    buyer_tax_id = Column(String(25), nullable=True)
    buyer_address = Column(String(200), nullable=True)
    buyer_phone = Column(String(50), nullable=True)
    buyer_bank = Column(String(100), nullable=True)
    buyer_account = Column(String(50), nullable=True)
    
    seller_name = Column(String(200), nullable=True)
    seller_tax_id = Column(String(25), nullable=True)
    seller_address = Column(String(200), nullable=True)
    seller_phone = Column(String(50), nullable=True)
    seller_bank = Column(String(100), nullable=True)
    seller_account = Column(String(50), nullable=True)
    
    total_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    amount_without_tax = Column(Float, nullable=True)
    amount_in_words = Column(String(100), nullable=True)
    
    check_code = Column(String(30), nullable=True)
    currency = Column(String(10), default="CNY")
    remarks = Column(Text, nullable=True)
    
    bank_name = Column(String(200), nullable=True)
    transaction_reference = Column(String(50), nullable=True)
    transaction_date = Column(String(20), nullable=True)
    transaction_time = Column(String(20), nullable=True)
    transaction_type = Column(String(50), nullable=True)
    
    source_account = Column(String(50), nullable=True)
    source_account_name = Column(String(200), nullable=True)
    source_bank = Column(String(200), nullable=True)
    
    receiver_account = Column(String(50), nullable=True)
    receiver_account_name = Column(String(200), nullable=True)
    receiver_bank = Column(String(200), nullable=True)
    
    is_invoice = Column(Boolean, default=True)
    invoice_confidence = Column(Float, default=0.0)
    extraction_confidence = Column(Float, default=0.0)
    validation_score = Column(Float, default=0.0)
    validation_errors = Column(JSON, nullable=True)
    validation_warnings = Column(JSON, nullable=True)
    
    raw_ocr_text = Column(Text, nullable=True)
