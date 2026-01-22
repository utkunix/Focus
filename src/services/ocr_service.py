import pytesseract
from PIL import Image, ImageOps, ImageStat
import sys

class OCRService:
    def __init__(self, lang='tur+eng'):
        self.lang = lang
        
        if sys.platform.startswith("win"):
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.join(os.getenv('LOCALAPPDATA', ''), r'Tesseract-OCR\tesseract.exe')
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"[OCR Service] Windows modu: Tesseract {path} adresinde bulundu.")
                    break
                          
    def image_to_text(self, image: Image):
        """
        Adımlar: Gri Ton -> Ters Çevir (Koyu Temaysa) -> Büyüt -> Eşikle -> Çerçevele
        """
        try:
            gray_image = image.convert('L')
            stat = ImageStat.Stat(gray_image)
            avg_brightness = stat.mean[0]

            if avg_brightness < 128:
                gray_image = ImageOps.invert(gray_image)

            new_size = tuple(3 * x for x in gray_image.size)
            processed_image = gray_image.resize(new_size, Image.Resampling.LANCZOS)

            processed_image = ImageOps.expand(processed_image, border=20, fill='white')

            processed_image.save("debug_ocr.png")

            config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed_image, lang=self.lang, config=config)
            return text.strip()
            
        except Exception as e:
            print(f"[OCR Hatası] Metin okunamadı: {e}")
            if sys.platform.startwith("win"):
                print("İPUCU: Windows'ta Tesseract yüklü mü? Path'e eklendi mi ?")
            return ""
