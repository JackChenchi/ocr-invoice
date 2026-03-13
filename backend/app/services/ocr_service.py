import os
import logging
from typing import Dict, Any, Optional, List
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

from app.core.config import settings

logger = logging.getLogger(__name__)

_ocr_instances = {}

def _get_ocr_instance(lang: str):
    global _ocr_instances
    if lang not in _ocr_instances:
        from paddleocr import PaddleOCR
        _ocr_instances[lang] = PaddleOCR(lang=lang)
    return _ocr_instances[lang]

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
    
    return avg_confidence > 0.6 and text_count > 8


def _score_ocr_result(result) -> float:
    if not result or not result[0]:
        return 0.0
    text_count = 0
    total_confidence = 0.0
    total_chars = 0
    for line in result[0]:
        if line and len(line) >= 2:
            text = line[1][0]
            confidence = line[1][1]
            if text and text.strip():
                text_count += 1
                total_confidence += confidence
                total_chars += len(text.strip())
    if text_count == 0:
        return 0.0
    avg_confidence = total_confidence / text_count
    length_factor = min(1.0, total_chars / 200.0)
    return avg_confidence * (0.5 + 0.5 * length_factor)

class OCRService:
    @staticmethod
    def process_image(image_path: str, lang: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found at {image_path}")

            if lang:
                langs: List[str] = [lang]
            else:
                langs = [l.strip() for l in settings.OCR_LANGS.split(",") if l.strip()]
                if not langs:
                    langs = ["ch"]

            best_result = None
            best_score = 0.0
            for l in langs:
                ocr = _get_ocr_instance(l)
                result = ocr.ocr(image_path)
                score = _score_ocr_result(result)
                if score > best_score:
                    best_score = score
                    best_result = result
            
            result = best_result
            
            preprocessed_path = None
            if not _is_ocr_result_good(result):
                preprocessed_path = _preprocess_image(image_path)
                if preprocessed_path != image_path:
                    best_result = None
                    best_score = 0.0
                    for l in langs:
                        ocr = _get_ocr_instance(l)
                        preprocessed_result = ocr.ocr(preprocessed_path)
                        score = _score_ocr_result(preprocessed_result)
                        if score > best_score:
                            best_score = score
                            best_result = preprocessed_result
                    if best_result and _is_ocr_result_good(best_result):
                        result = best_result
            
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
