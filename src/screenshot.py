import os
import sys
import time
from datetime import datetime
from io import BytesIO
from typing import List, Tuple

from PIL import Image
from progress.bar import Bar
from PyQt6.QtCore import QBuffer, QIODevice, QObject, QPoint, QStandardPaths, Qt
from PyQt6.QtGui import QColor, QCursor, QGuiApplication, QPainter, QPen, QPixmap


class ScreenShot(QObject):
    def __init__(self, parent=None, fps=1, max_sec=60):
        super(ScreenShot, self).__init__(parent)
        self.screen = QGuiApplication.primaryScreen()
        self.interval_sec = 1 / fps
        self.max_sec = max_sec
        self.parent_widget = parent

    def get_screen_info(self, rect):
        cursor_pos = QCursor.pos()
        screen_pixmap = self.screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        cursor_pos = QPoint(cursor_pos.x() - rect.x(), cursor_pos.y() - rect.y())
        return screen_pixmap, cursor_pos

    def create_gif(self, screen_info: List[Tuple[QPixmap, QPoint]], duration: int):
        pen = QPen()
        pen.setWidth(7)
        pen.setColor(QColor(Qt.GlobalColor.red))

        images = []
        suffix = "[%(elapsed_td)s>%(eta_td)s]"

        for value in Bar("Taking screenshots", suffix=suffix, empty_fill=chr(0xFFEE), fill=chr(0xFFED), file=sys.stdout, check_tty=False).iter(screen_info):
            pixmap, point = value
            paint = QPainter()
            paint.begin(pixmap)
            paint.setPen(pen)
            paint.drawEllipse(point, 10, 10)
            paint.end()
            image_buffer = QBuffer()
            image_buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            pixmap.save(image_buffer, format="PNG")
            images.append(Image.open(BytesIO(image_buffer.data())))

        output_path = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation), f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H.%M.%S')}.gif"
        )
        images[0].save(output_path, save_all=True, append_images=images, optimize=False, duration=duration * 1000, loop=0)
        return output_path

    def run(self, worker_object, rect):
        screen_info = []
        print(f"Start recording {self.max_sec} seconds")
        print("Use the Finish button to stop recording.")

        suffix = "[%(elapsed_td)s>%(eta_td)s]"
        for _ in Bar("Taking screenshots", suffix=suffix, empty_fill=chr(0xFFEE), fill=chr(0xFFED), file=sys.stdout, check_tty=False).iter(
            range(int(self.max_sec / self.interval_sec))
        ):
            if worker_object.is_stop:
                break
            start = time.time()
            screen_info.append(self.get_screen_info(rect))
            elapsed_time = time.time() - start

            while elapsed_time < self.interval_sec:
                time.sleep(self.interval_sec / 10)
                elapsed_time = time.time() - start
        print("Creating GIF files...")
        return self.create_gif(screen_info, duration=self.interval_sec)

    def result_thread(self, message):
        order, image = message
        self.images[order] = image
