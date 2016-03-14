import abc
from PyQt5 import QtCore

class Base(object):
    __metaclass__ = abc.ABCMeta

    continueOnFailure = False

    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def getWorker(self, window):
        pass

class BaseWorker(QtCore.QObject):
    timeout = 10
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(bool)

    @abc.abstractmethod
    @QtCore.pyqtSlot()
    def start():
        """ This function needs to emit finished signal """
        pass

class worker(BaseWorker):

    @QtCore.pyqtSlot()
    def start(self):
        QtCore.QThread.sleep(1)
        self.progress.emit(50)
        QtCore.QThread.sleep(1)
        self.progress.emit(50)
        QtCore.QThread.sleep(1)
        self.finished.emit(True)


class Simple(Base):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def getWorker(self):

        return worker()


WORKFLOW = (
    Simple("POWER"),
    Simple("ATSHA"),
    Simple("UBOOT"),
    Simple("REBOOT"),
    Simple("REFLASH"),
    Simple("RTC"),
)

