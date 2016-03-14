from PyQt5 import QtCore

from workflow.base import Base, BaseWorker


class SimpleTest(Base):

    continueOnFailure = True

    def __init__(self, name, result):
        self._name = name
        self.result = result

    def getWorker(self):
        return SimpleTestWorker(self.result)


class SimpleTestWorker(BaseWorker):
    def __init__(self, result):
        super(SimpleTestWorker, self).__init__()
        self.result = result

    @QtCore.pyqtSlot()
    def start(self):
        for i in range(0, 100, 10):
            QtCore.QThread.msleep(100)
            self.progress.emit(10)
            QtCore.QThread.msleep(100)
        self.finished.emit(self.result)



TESTS = (
    SimpleTest("USB", True),
    SimpleTest("PCIA", True),
    SimpleTest("THERMOMETER", False),
    SimpleTest("GPIO", True),
    SimpleTest("CLOCK", False),
)

