import sys

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QMessageBox, QRubberBand, QVBoxLayout


class RubberBandArea(QDialog):
    # Use RubberBand to select a rectangle.
    rect_selected = pyqtSignal(QRect)

    def __init__(self):
        super(RubberBandArea, self).__init__()

        # 非同期処理中の標準出力を表示エリア（ReadOnly）
        # Widgetを配置
        main_layout = QVBoxLayout()
        font = self.font()
        font.setPointSize(100)
        label = QLabel("Drag & drop to select")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        label.setFont(font)
        main_layout.addWidget(label)
        self.setLayout(main_layout)

        self.screen_rect = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(0, 0, self.screen_rect.width(), self.screen_rect.height())
        self.setWindowOpacity(0.3)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.rubberband = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.setMouseTracking(True)
        self._rect = None
        self.is_redraw = None

    @property
    def selected_rect(self):
        if self._rect is None:
            self._rect = self.screen_rect
        return QRect(self._rect.x(), self._rect.y() + self.geometry().y(), self._rect.width(), self._rect.height())

    def keyPressEvent(self, event):
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            result = QMessageBox.question(None, "", "Take a screenshot of the full screen?", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
            if result == QMessageBox.StandardButton.Ok:
                self.accept()
        QDialog.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        self.origin = event.position().toPoint()
        self.rubberband.setGeometry(QRect(self.origin, QSize()))
        self.rubberband.show()
        QDialog.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(QRect(self.origin, event.position().toPoint()).normalized())
        QDialog.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            QDialog.mouseReleaseEvent(self, event)
            self._rect = QRect(rect.x(), rect.y(), rect.width(), rect.height())
            if self._rect.isEmpty() or self._rect.width() < 0 or self._rect.height() < 0:
                return
            self.is_redraw = True
            self.update()
            result = QMessageBox.question(None, "", "Take a screenshot of the selected area?", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
            if result == QMessageBox.StandardButton.Ok:
                self.accept()
        else:
            QDialog.mouseReleaseEvent(self, event)

    def paintEvent(self, event):
        if self.is_redraw:
            paint = QPainter(self)
            pen = QPen()
            pen.setWidth(7)
            pen.setColor(QColor(Qt.GlobalColor.red))
            paint.setPen(pen)
            paint.drawRect(self._rect)
            self.is_redraw = False
