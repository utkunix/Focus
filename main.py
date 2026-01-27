import sys
import os
import platform
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QVBoxLayout, QWidget, QTextEdit, QMessageBox, QComboBox, QInputDialog
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer

from src.ui.selector import SelectionOverlay
from src.services.capture_service import CaptureService
from src.services.ocr_service import OCRService
from src.services.ai_service import AIService

class FirstRunWizard:
    @staticmethod
    def check_api_key():
        """
        API anahtarı yoksa kullanıcıyı siteye yönlendirir ve anahtarı alıp .env dosyasına kaydeder.
        """
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                content = f.read()
                if "GROQ_API_KEY" in content and "gsk_" in content:
                    return True

        msg = QMessageBox()
        msg.setWindowTitle("Focus - İlk Kurulum")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Hoş Geldiniz! Focus'u kullanmak için ücretsiz bir API Anahtarı gereklidir.")
        msg.setInformativeText("Henüz bir anahtarınız yoksa, aşağıdan siteye gidip ücretsiz alabilirsiniz.\n\nSite: console.groq.com/keys")

        btn_get_key = msg.addButton("🌐 Siteyi Aç (Anahtar Al)", QMessageBox.ButtonRole.ActionRole)
        btn_enter_key = msg.addButton("🔑 Anahtarım Var", QMessageBox.ButtonRole.AcceptRole)
        
        msg.exec()
        
        if msg.clickedButton() == btn_get_key:
            webbrowser.open("https://console.groq.com/keys")
        
        key, ok = QInputDialog.getText(
            None, 
            "API Anahtarı Girişi", 
            "Lütfen 'gsk_' ile başlayan anahtarınızı aşağıya yapıştırın:",
            text=""
        )
        
        if ok and key and key.strip():
            with open(env_path, "w") as f:
                f.write(f"GROQ_API_KEY={key.strip()}")
            
            os.environ["GROQ_API_KEY"] = key.strip()
            
            QMessageBox.information(None, "Başarılı", "Kurulum tamamlandı! Focus açılıyor...")
            return True
        else:
            QMessageBox.critical(None, "Hata", "API anahtarı girilmediği için uygulama başlatılamıyor.")
            sys.exit()

    @staticmethod
    def check_tesseract():
        """
        Tesseract kontrolü (Değişiklik yok, aynen kalabilir)
        """
        try:
            import pytesseract
            if platform.system() == "Windows":
                 paths = [
                     r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                     r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                     os.path.join(os.getenv('LOCALAPPDATA', ''), r'Tesseract-OCR\tesseract.exe')
                 ]
                 for p in paths:
                     if os.path.exists(p):
                         pytesseract.pytesseract.tesseract_cmd = p
                         break
            
            pytesseract.get_tesseract_version()
            return True
        except Exception:

            pass


class FocusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus - AI Exam Helper")
        self.setGeometry(100, 100, 550, 750)
        
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.capture_service = CaptureService()
        self.ocr_service = OCRService()
        self.ai_service = AIService()
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.status_label = QLabel("Başlamak için bir alan seçin...")
        self.status_label.setStyleSheet("font-size: 15px; color: #34495e; font-weight: bold; padding: 5px;")
        
        self.psm_label = QLabel("Okuma Modu (OCR Hassasiyeti):")
        self.psm_combo = QComboBox()
        self.psm_combo.addItems([
            "Otomatik Analiz (PSM 3)", 
            "Tek Metin Bloğu (PSM 6)", 
            "Tek Satır (PSM 7)"
        ])
        self.psm_combo.setCurrentIndex(1)

        self.btn_select = QPushButton("Soru Seç ve Çöz")
        self.btn_select.setStyleSheet("""
            QPushButton { background-color: #2c3e50; color: white; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background-color: #34495e; }
        """)
        self.btn_select.clicked.connect(self.start_selection)
        
        self.lbl_ocr = QLabel("Okunan Metin:")
        self.text_output = QTextEdit()
        self.text_output.setMaximumHeight(100)
        
        self.lbl_ai = QLabel("Yapay Zeka Çözümü:")
        self.text_ai = QTextEdit()
        self.text_ai.setPlaceholderText("Cevap bekleniyor...")
        self.text_ai.setStyleSheet("""
            QTextEdit { font-size: 15px; color: #2c3e50; background-color: #fdfefe; border: 2px solid #27ae60; border-radius: 10px; padding: 10px; }
        """)

        self.btn_copy = QPushButton("Çözümü Panoya Kopyala")
        self.btn_copy.setStyleSheet("""
            QPushButton { background-color: #95a5a6; color: white; padding: 10px; font-size: 13px; font-weight: bold; border-radius: 5px; margin-top: 5px; }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)

        layout.addWidget(self.status_label)
        layout.addWidget(self.psm_label)
        layout.addWidget(self.psm_combo)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.lbl_ocr)
        layout.addWidget(self.text_output)
        layout.addWidget(self.lbl_ai)
        layout.addWidget(self.text_ai)
        layout.addWidget(self.btn_copy)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_selection(self):
        self.selector = SelectionOverlay()
        self.selector.selection_completed.connect(self.on_selection_done)
        self.selector.show()

    def on_selection_done(self, coords):
        x, y, w, h = coords
        scale_factor = QApplication.primaryScreen().devicePixelRatio()
        
        self.status_label.setText("Görsel işleniyor...")
        self.status_label.setStyleSheet("color: #2980b9; font-weight: bold;")
        self.text_output.clear()
        self.text_ai.clear()
        QApplication.processEvents()

        try:
            image = self.capture_service.capture_region(x, y, w, h, scale_factor=scale_factor)
            
            psm_map = {0: 3, 1: 6, 2: 7}
            selected_psm = psm_map[self.psm_combo.currentIndex()]
            
            ocr_text = self.ocr_service.image_to_text(image, psm=selected_psm)
            self.text_output.setText(ocr_text)
            
            if not ocr_text or "Hata:" in ocr_text:
                self.status_label.setText("Hata: Metin okunamadı.")
                self.status_label.setStyleSheet("color: #c0392b; font-weight: bold;")
                return

            self.status_label.setText("Yapay Zeka cevap hazırlıyor...")
            QApplication.processEvents()

            answer = self.ai_service.get_answer(ocr_text)
            
            if answer.startswith("Hata:"):
                self.status_label.setText("AI Yanıt Veremedi.")
                self.status_label.setStyleSheet("color: #c0392b; font-weight: bold;")
            else:
                self.text_ai.setMarkdown(answer)
                self.status_label.setText("İşlem Başarılı.")
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Beklenmedik Hata", str(e))
            self.status_label.setText("Sistem hatası.")

    def copy_to_clipboard(self):
        text = self.text_ai.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            original_status = self.status_label.text()
            original_style = self.status_label.styleSheet()
            
            self.status_label.setText("✅ Çözüm panoya kopyalandı!")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            QTimer.singleShot(2000, lambda: self.reset_status(original_status, original_style))

    def reset_status(self, text, style):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(style)

def main():
    app = QApplication(sys.argv)
    window = FocusApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    FirstRunWizard.check_tesseract()
    
    FirstRunWizard.check_api_key()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
