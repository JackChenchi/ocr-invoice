import os
from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.orm import Session

from app.models.ocr import InvoiceResult, OCRResult


def cleanup_old_records(
    db: Session,
    data_retention_days: int,
    image_retention_days: int
) -> Dict[str, int]:
    now = datetime.utcnow()
    data_cutoff = now - timedelta(days=data_retention_days)
    image_cutoff = now - timedelta(days=image_retention_days)

    deleted_images = 0
    nulled_images = 0
    deleted_invoices = 0
    deleted_ocr = 0

    # Remove old images but keep record
    old_images = db.query(InvoiceResult).filter(
        InvoiceResult.upload_time < image_cutoff,
        InvoiceResult.image_url.isnot(None),
        InvoiceResult.image_url != ""
    ).all()
    for inv in old_images:
        if inv.image_url and os.path.exists(inv.image_url):
            try:
                os.remove(inv.image_url)
                deleted_images += 1
            except Exception:
                pass
        inv.image_url = None
        nulled_images += 1

    # Delete very old records
    old_invoices = db.query(InvoiceResult).filter(InvoiceResult.upload_time < data_cutoff).all()
    for inv in old_invoices:
        if inv.image_url and os.path.exists(inv.image_url):
            try:
                os.remove(inv.image_url)
                deleted_images += 1
            except Exception:
                pass
        db.delete(inv)
        deleted_invoices += 1

    old_ocr = db.query(OCRResult).filter(OCRResult.upload_time < data_cutoff).all()
    for rec in old_ocr:
        if rec.image_url and os.path.exists(rec.image_url):
            try:
                os.remove(rec.image_url)
                deleted_images += 1
            except Exception:
                pass
        db.delete(rec)
        deleted_ocr += 1

    db.commit()

    return {
        "deleted_images": deleted_images,
        "nulled_images": nulled_images,
        "deleted_invoices": deleted_invoices,
        "deleted_ocr": deleted_ocr
    }
