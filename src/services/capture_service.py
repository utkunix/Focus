import mss
from PIL import Image

class CaptureService:
    def __init__(self):
        self.sct = mss.mss()
        self.y_correction = 30 #geçici

    def capture_region(self, x, y, w, h, scale_factor=1.0):

        phys_x = int(x * scale_factor)
        phys_y = int(y * scale_factor)
        phys_w = int(w * scale_factor)
        phys_h = int(h * scale_factor)
        
        corrected_y = phys_y + self.y_correction
        
        print(f"[Capture] Orjinal Y: {phys_y} -> Düzeltilmiş Y: {corrected_y} (Offset: +{self.y_correction})")
        
        monitor = {"top": corrected_y, "left": phys_x, "width": phys_w, "height": phys_h}
        
        sct_img = self.sct.grab(monitor)
        
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        return img
