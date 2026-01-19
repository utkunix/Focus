import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from src.ui.selector import SelectionOverlay

class FocusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus - Exam Helper")
        self.setGeometry(100, 100, 400, 300)
        
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
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.btn_select)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_selection(self):
        self.selector = SelectionOverlay()
        self.selector.selection_completed.connect(self.on_selection_done)
        self.selector.show()

    def on_selection_done(self, coords):
        x, y, w, h = coords
        print(f"[DEBUG] Seçilen Koordinatlar: X={x}, Y={y}, W={w}, H={h}")
        self.status_label.setText(f"Seçim: {x}, {y} | {w}x{h} px")
        
        # BİR SONRAKİ ADIMDA BURADA:
        # capture_service.take_screenshot(coords) çağırılacak.

def main():
    app = QApplication(sys.argv)
    window = FocusApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
