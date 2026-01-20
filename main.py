import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTextEdit
from src.ui.selector import SelectionOverlay
from src.services.capture_service import CaptureService
from src.services.ocr_service import OCRService

class FocusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus - Exam Helper")
        self.setGeometry(100, 100, 500, 400)

        self.capture_service = CaptureService()
        self.ocr_service = OCRService()
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Bir alan seçin...")
        self.status_label.setStyleSheet("font-size: 16px; color: #333;")
        
        self.btn_select = QPushButton("Soru Seç (Snipping Tool)")
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
        
        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("Seçtiğin alandaki metin burada belirecek...")
        self.text_output.setStyleSheet("font-size: 14px; padding: 5px;")

        layout.addWidget(self.status_label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.text_output)
        
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
        QApplication.processEvents()

        try:
            image = self.capture_service.capture_region(x, y, w, h, scale_factor=scale_factor)
            
            image.save("debug_capture.png")
            
            ocr_text = self.ocr_service.image_to_text(image)
            self.text_output.setText(ocr_text)
            
            self.status_label.setText("İşlem Tamamlandı.")
            print(f"[OCR SONUÇ]:\n{ocr_text}")
            
        except Exception as e:
            self.status_label.setText("Hata oluştu!")
            self.text_output.setText(f"Hata detayı: {str(e)}")
            print(f"[ERROR] {e}")

def main():
    app = QApplication(sys.argv)
    window = FocusApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
