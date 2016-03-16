import abc
import pexpect
from PyQt5 import QtCore


class Base(object):
    __metaclass__ = abc.ABCMeta

    continueOnFailure = False

    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def createWorker(self):
        pass

    def getWorker(self, logfile):
        worker = self.createWorker()
        setattr(worker, 'name', self.name)
        setattr(worker, 'logfile', logfile)
        return worker

class BaseTest(Base):
    continueOnFailure = True


class BaseWorker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(bool)

    @abc.abstractmethod
    def perform(self):
        pass

    @QtCore.pyqtSlot()
    def start(self):
        with open(self.logfile, 'a') as self.log:
            self.log.write("\n########## %s ##########\n" % self.name)
            try:
                # open log file
                retval = self.perform()
            except pexpect.TIMEOUT:
                self.log.write("\n>>>>>>>>>> TIMEOUT <<<<<<<<<<\n")
                retval = False
            except Exception:
                self.log.write("\n>>>>>>>>>> ERROR <<<<<<<<<<\n")
                retval = False
            if retval:
                self.log.write("\n---------- %s ----------\n" % self.name)
            else:
                self.log.write("\n!!!!!!!!!! %s !!!!!!!!!!\n" % self.name)

        self.finished.emit(True if retval else False)  # Boolean needs to be emitted
