import sys

from progress import HIDE_CURSOR, SHOW_CURSOR
from PyQt6.QtCore import Q_ARG, QMetaObject, QObject, Qt, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from src.rubber_band import RubberBandArea
from src.screenshot import ScreenShot
from src.thread_worker import Worker


class WorkerSignals(QObject):
    finish = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)


class CustomPlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(CustomPlainTextEdit, self).__init__(parent=parent)
        self.is_progress_bar = False

    def write(self, message):
        # Support for "progress" module
        message = message.strip()
        if message == SHOW_CURSOR:
            self.is_progress_bar = False
            return
        if message:
            if self.is_progress_bar:
                QMetaObject.invokeMethod(self, "replace_last_line", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))
            else:
                QMetaObject.invokeMethod(self, "appendPlainText", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))
        if message == HIDE_CURSOR:
            self.is_progress_bar = True
            return

    @pyqtSlot(str)
    def replace_last_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertBlock()
        self.setTextCursor(cursor)
        self.insertPlainText(text)

    def flush(self):
        pass


class MainWindow(QMainWindow):
    stop_worker = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # Configure GUI components
        self.set_gui()
        # Required for asynchronous processing
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

        self.total_time = 30

    def set_gui(self):
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_button_clicked)
        self.stop_button = QPushButton("Finish")
        self.stop_button.clicked.connect(self.stop_button_pushed)

        self.fps_spin_box = QSpinBox()
        self.fps_spin_box.setMinimum(1)
        self.fps_spin_box.setMaximum(9)
        self.fps_spin_box.setValue(3)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        self.text_area = CustomPlainTextEdit()
        self.text_area.setReadOnly(True)
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(QLabel("fps"))
        h_layout.addWidget(self.fps_spin_box)
        h_layout.addWidget(self.start_button)
        h_layout.addWidget(self.stop_button)
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.text_area)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setWindowTitle("Snapshot GIF")
        self.resize(600, 300)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        # Do not close the application while asynchronous processing is running.
        if self.thread_pool.activeThreadCount() > 0:
            QMessageBox.information(None, "", "Processing is in progress", QMessageBox.StandardButton.Ok)
            event.ignore()
        else:
            event.accept()

    def start_button_clicked(self):
        if self.thread_pool.activeThreadCount() == 0:
            self.rubber_band = RubberBandArea()
            if self.rubber_band.exec() == QDialog.DialogCode.Accepted:
                # Change the output destination to text_are
                self.old_stdout = sys.stdout
                sys.stdout = self.text_area
                # Control Button
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)

                fps = self.fps_spin_box.value()
                worker = Worker(ScreenShot(self, fps, self.total_time).run, rect=self.rubber_band.selected_rect)
                self.stop_worker.connect(worker.stop)
                worker.signals.finish.connect(self.finish_thread)
                worker.signals.error.connect(self.error_thread)
                worker.signals.result.connect(self.result_thread)
                self.thread_pool.start(worker)

    def stop_button_pushed(self):
        if self.thread_pool.activeThreadCount() > 0:
            print("Request to suspend processing")
            self.stop_button.setEnabled(False)
            self.stop_worker.emit()

    def error_thread(self, message):
        print("Outputs error logs that occur in asynchronous processing")
        print(message)

    def result_thread(self, message):
        print(f"Output file: {message}")

    def finish_thread(self):
        self.thread_pool.waitForDone()
        self.thread_pool.clear()
        sys.stdout = self.old_stdout
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
