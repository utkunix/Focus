import pytesseract
import sys
import os
import cv2
import numpy as np
from PIL import Image

class OCRService:
    def __init__(self, lang='tur+eng'):
        self.lang = lang
        if sys.platform.startswith("win"):
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def find_text_bounds(self, thresh_img):
        """Metnin bulunduğu en küçük çerçeveyi tespit eder (Auto-Crop)."""
        coords = cv2.findNonZero(255 - thresh_img)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            return x, y, w, h
        return None

    def preprocess_image(self, pil_image):
        open_cv_image = np.array(pil_image.convert('RGB'))
        img = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        bounds = self.find_text_bounds(thresh)
        if bounds:
            x, y, w, h = bounds
            padding = 15
            x, y = max(0, x - padding), max(0, y - padding)
            w, h = w + (padding * 2), h + (padding * 2)
            thresh = thresh[y:y+h, x:x+w]

        scaled = cv2.resize(thresh, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        return scaled

    def image_to_text(self, image: Image, psm=6):
        try:
            processed_img = self.preprocess_image(image)
            cv2.imwrite("debug_ocr_processed.png", processed_img)

            config = f'--oem 3 --psm {psm}'
            text = pytesseract.image_to_string(processed_img, lang=self.lang, config=config)
            return text.strip()
            
        except Exception as e:
            return f"Hata: OCR okunurken bir sorun oluştu. ({str(e)})"
