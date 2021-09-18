import traceback

from PyQt6.QtCore import QMutex, QMutexLocker, QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    finish = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, fn_run, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn_run = fn_run
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.mutex = QMutex()
        self.is_stop = False

    @pyqtSlot()
    def run(self):
        try:
            with QMutexLocker(self.mutex):
                self.is_stop = False
            result = self.fn_run(self, *self.args, **self.kwargs)
        except:
            traceback.print_exc()
            self.signals.error.emit(traceback.format_exc())
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finish.emit()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.is_stop = True
