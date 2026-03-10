import os
import logging
from typing import Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

logger = logging.getLogger(__name__)

_ocr_instance = None

def _get_ocr_instance():
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR
        _ocr_instance = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            use_gpu=False,
            show_log=False
        )
    return _ocr_instance

def _preprocess_image(image_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    
    height, width = img.shape[:2]
    
    if height >= 800 and width >= 800:
        return image_path
    
    preprocessed_path = image_path.replace('.jpg', '_preprocessed.jpg').replace('.png', '_preprocessed.png')
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    scale_factor = max(800 / height, 800 / width)
    if scale_factor > 1.5:
        gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
    
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    cv2.imwrite(preprocessed_path, binary)
    
    return preprocessed_path

def _is_ocr_result_good(result) -> bool:
    if not result or not result[0]:
        return False
    
    text_count = 0
    total_confidence = 0
    
    for line in result[0]:
        if line and len(line) >= 2:
            text = line[1][0]
            confidence = line[1][1]
            if text and text.strip():
                text_count += 1
                total_confidence += confidence
    
    if text_count < 5:
        return False
    
    avg_confidence = total_confidence / text_count if text_count > 0 else 0
    
    return avg_confidence > 0.7 and text_count > 10

class OCRService:
    @staticmethod
    def process_image(image_path: str, lang: str = 'en') -> Dict[str, Any]:
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found at {image_path}")

            ocr = _get_ocr_instance()
            
            result = ocr.ocr(image_path, cls=True)
            
            preprocessed_path = None
            if not _is_ocr_result_good(result):
                preprocessed_path = _preprocess_image(image_path)
                if preprocessed_path != image_path:
                    preprocessed_result = ocr.ocr(preprocessed_path, cls=True)
                    if _is_ocr_result_good(preprocessed_result):
                        result = preprocessed_result
            
            if preprocessed_path and preprocessed_path != image_path and os.path.exists(preprocessed_path):
                try:
                    os.remove(preprocessed_path)
                except:
                    pass
            
            if not result or not result[0]:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "raw_data": {}
                }
            
            text_parts = []
            total_confidence = 0
            valid_count = 0
            
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    if text and text.strip():
                        text_parts.append(text.strip())
                        total_confidence += confidence
                        valid_count += 1
            
            full_text = " ".join(text_parts)
            avg_confidence = (total_confidence / valid_count) if valid_count > 0 else 0.0
            
            return {
                "text": full_text,
                "confidence": avg_confidence,
                "raw_data": result
            }

        except Exception as e:
            logger.error(f"OCR processing failed for {image_path}: {str(e)}")
            raise e

ocr_service = OCRService()
