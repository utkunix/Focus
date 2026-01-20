import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt6.QtGui import QIcon
import os
from src.ui.selector import SelectionOverlay
from src.services.capture_service import CaptureService
from src.services.ocr_service import OCRService
from src.services.ai_service import AIService

class FocusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus - Exam Helper")
        self.setGeometry(100, 100, 500, 600)
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.capture_service = CaptureService()
        self.ocr_service = OCRService()
        self.ai_service = AIService()
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Bir alan seçin...")
        self.status_label.setStyleSheet("font-size: 16px; color: #333;")
        
        
        self.btn_select = QPushButton("Soru Seç ve Çöz")
        self.btn_select.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        self.btn_select.clicked.connect(self.start_selection)
        
        self.lbl_ocr = QLabel("Okunan Metin:")
        self.text_output = QTextEdit()
        self.text_output.setMaximumHeight(100)
        self.text_output.setPlaceholderText("Seçtiğin alandaki metin burada belirecek...")
        self.text_output.setStyleSheet("font-size: 14px; padding: 5px;")

        self.lbl_ai = QLabel("Yapay Zeka Cevabı:")
        self.text_ai = QTextEdit()
        self.text_ai.setPlaceholderText("Cevap burada belirecek...")
        self.text_ai.setStyleSheet("font-size: 15px; color: #2c3e50; background-color: #f4f6f7; border: 2px solid #27ae60; border-radius: 8px; padding: 10px;")

        layout.addWidget(self.status_label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.lbl_ocr)
        layout.addWidget(self.text_output)
        layout.addWidget(self.lbl_ai)
        layout.addWidget(self.text_ai)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_selection(self):
        self.selector = SelectionOverlay()
        self.selector.selection_completed.connect(self.on_selection_done)
        self.selector.show()

    def on_selection_done(self, coords):
        x, y, w, h = coords
        
        screen = QApplication.primaryScreen()
        scale_factor = screen.devicePixelRatio()
        
        self.status_label.setText(f"İşleniyor (Scale: {scale_factor})...")
        self.text_output.clear()
        self.text_ai.clear()
        QApplication.processEvents()

        try:
            image = self.capture_service.capture_region(x, y, w, h, scale_factor=scale_factor)
            image.save("debug_capture.png")
            
            ocr_text = self.ocr_service.image_to_text(image)
            self.text_output.setText(ocr_text)
            
            if not ocr_text.strip():
                self.status_label.setText("Metin bulunamadı!")
                return

            self.status_label.setText("Yapay Zeka Düşünüyor...")
            QApplication.processEvents()

            answer = self.ai_service.get_answer(ocr_text)
            self.text_ai.setText(answer)
            
            self.status_label.setText("İşlem Tamamlandı.")
            print(f"[AI Cevabı]: {answer}")
            
        except Exception as e:
            self.status_label.setText("Hata oluştu!")
            self.text_ai.setText(f"Hata detayı: {str(e)}")
            print(f"[ERROR] {e}")

def main():
    app = QApplication(sys.argv)
    window = FocusApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
