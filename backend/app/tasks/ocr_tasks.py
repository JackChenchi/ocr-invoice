from celery import shared_task
from app.db.session import SessionLocal
from app.models.ocr import OCRResult, OCRStatus
from app.services.ocr_service import ocr_service
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_image_task(ocr_result_id: int):
    db = SessionLocal()
    try:
        # 1. 获取任务记录
        ocr_result = db.query(OCRResult).filter(OCRResult.id == ocr_result_id).first()
        if not ocr_result:
            return f"Task {ocr_result_id} not found"

        # 2. 更新状态为 Processing
        ocr_result.status = OCRStatus.PROCESSING
        db.commit()

        # 3. 调用真实 OCR 服务
        start_time = time.time()
        
        # 获取图片路径 (假设 image_url 是本地文件路径)
        image_path = ocr_result.image_url
        
        # 执行 OCR
        # 注意：如果是 Windows 路径，pytesseract 通常能处理，但确保路径是绝对路径
        result = ocr_service.process_image(image_path)
        
        # 4. 更新结果
        ocr_result.ocr_text = result["text"]
        ocr_result.confidence = result["confidence"]
        ocr_result.process_time = time.time() - start_time
        ocr_result.status = OCRStatus.COMPLETED
        # ocr_result.coordinates = result.get("raw_data") # 如果需要保存坐标信息
        
        db.commit()
        
        return f"Task {ocr_result_id} completed"

    except Exception as e:
        logger.error(f"Task {ocr_result_id} failed: {e}")
        if ocr_result:
            ocr_result.status = OCRStatus.FAILED
            ocr_result.error_msg = str(e)
            db.commit()
        return f"Task {ocr_result_id} failed: {str(e)}"
    finally:
        db.close()
