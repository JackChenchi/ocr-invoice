import cv2
import numpy as np
from PIL import Image
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot load image from {image_path}")
        return image

    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            return clahe.apply(image)

    @staticmethod
    def sharpen_for_sans_serif(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        kernel_sharpen = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        sharpened = cv2.filter2D(gray, -1, kernel_sharpen)
        
        if len(image.shape) == 3:
            return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        return sharpened

    @staticmethod
    def adaptive_threshold(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        if len(image.shape) == 3:
            return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        return binary

    @staticmethod
    def detect_skew_angle(image: np.ndarray) -> float:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilated = cv2.dilate(binary, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        angles = []
        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue
            rect = cv2.minAreaRect(contour)
            angle = rect[-1]
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90
            if abs(angle) < 45:
                angles.append(angle)
        
        if not angles:
            return 0.0
        
        return np.median(angles)

    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        if abs(angle) < 0.5:
            return image
        
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        matrix[0, 2] += (new_w / 2) - center[0]
        matrix[1, 2] += (new_h / 2) - center[1]
        
        rotated = cv2.warpAffine(image, matrix, (new_w, new_h), 
                                  flags=cv2.INTER_CUBIC, 
                                  borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def binarize(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    @staticmethod
    def remove_shadows(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        dilated = cv2.dilate(gray, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
        bg = cv2.medianBlur(dilated, 21)
        diff = 255 - cv2.absdiff(gray, bg)
        norm = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
        
        return norm

    @staticmethod
    def preprocess_for_ocr(image_path: str, output_path: Optional[str] = None, sharpen: bool = False) -> str:
        image = ImagePreprocessor.load_image(image_path)
        
        image = ImagePreprocessor.remove_shadows(image)
        
        angle = ImagePreprocessor.detect_skew_angle(image)
        if abs(angle) > 0.5:
            image = ImagePreprocessor.rotate_image(image, angle)
        
        image = ImagePreprocessor.denoise(image)
        image = ImagePreprocessor.enhance_contrast(image)
        
        if sharpen:
            image = ImagePreprocessor.sharpen_for_sans_serif(image)
        
        if output_path is None:
            import os
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_processed{ext}"
        
        cv2.imwrite(output_path, image)
        logger.info(f"Preprocessed image saved to {output_path}")
        
        return output_path

    @staticmethod
    def preprocess_image_array(image: np.ndarray) -> np.ndarray:
        image = ImagePreprocessor.remove_shadows(image)
        
        angle = ImagePreprocessor.detect_skew_angle(image)
        if abs(angle) > 0.5:
            image = ImagePreprocessor.rotate_image(image, angle)
        
        image = ImagePreprocessor.denoise(image)
        image = ImagePreprocessor.enhance_contrast(image)
        image = ImagePreprocessor.sharpen_for_sans_serif(image)
        
        return image

image_preprocessor = ImagePreprocessor()
