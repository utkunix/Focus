import sys
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class SelectionOverlay(QWidget):
    selection_completed = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        self.start_point = None
        self.end_point = None
        self.is_selecting = False
        
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        overlay_color = QColor(0, 0, 0, 150) 
        painter.fillRect(self.rect(), overlay_color)

        if self.start_point and self.end_point:
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.GlobalColor.transparent)
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_point = event.pos()
            self.is_selecting = False
            
            rect = QRect(self.start_point, self.end_point).normalized()
            
            if rect.width() > 5 and rect.height() > 5:
                coords = (rect.x(), rect.y(), rect.width(), rect.height())
                self.selection_completed.emit(coords)
                self.close()
            else:
                self.start_point = None
                self.end_point = None
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
