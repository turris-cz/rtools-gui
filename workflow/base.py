import abc
from PyQt5 import QtCore

class Base(object):
    __metaclass__ = abc.ABCMeta

    continueOnFailure = False

    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def getWorker(self):
        pass


class BaseWorker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(bool)

    @abc.abstractmethod
    @QtCore.pyqtSlot()
    def start(self):
        """ This function needs to emit finished signal """
        pass
