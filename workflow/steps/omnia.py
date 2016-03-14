from PyQt5 import QtCore

from workflow.base import Base, BaseWorker


class Simple(Base):

    def __init__(self, name):
        self._name = name

    def getWorker(self):
        return SimpleWorker()


class SimpleWorker(BaseWorker):

    @QtCore.pyqtSlot()
    def start(self):
        QtCore.QThread.sleep(1)
        self.progress.emit(50)
        QtCore.QThread.sleep(1)
        self.progress.emit(50)
        QtCore.QThread.sleep(1)
        self.finished.emit(True)


WORKFLOW = (
    Simple("POWER"),
    Simple("ATSHA"),
    Simple("UBOOT"),
    Simple("REBOOT"),
    Simple("REFLASH"),
    Simple("RTC"),
)
