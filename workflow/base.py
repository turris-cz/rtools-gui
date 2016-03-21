import abc
import os
import pexpect
import sys

from PyQt5 import QtCore

def spawnPexpectSerialConsole():
    return pexpect.spawn(os.path.join(sys.path[0], 'sc_connector.py'))

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
    firmware = QtCore.pyqtSignal(str)

    @abc.abstractmethod
    def perform(self):
        pass

    @QtCore.pyqtSlot()
    def start(self):
        self.expected = []
        with open(self.logfile, 'a') as self.log:
            self.log.write("\n########## %s ##########\n" % self.name)
            try:
                # open log file
                retval = self.perform()
            except pexpect.TIMEOUT:
                self.log.write("\n>>>>>>>>>> TIMEOUT '%s' <<<<<<<<<<\n" % str(self.expected))
                retval = False
            except Exception as e:
                self.log.write("\n>>>>>>>>>> ERROR '%s' <<<<<<<<<<\n" % e.message)
                retval = False
            if retval:
                self.log.write("\n---------- %s ----------\n" % self.name)
            else:
                self.log.write("\n!!!!!!!!!! %s !!!!!!!!!!\n" % self.name)

        self.finished.emit(True if retval else False)  # Boolean needs to be emitted

    def expect(self, exp, *args, **kwargs):
        self.expected = args[0]
        res = exp.expect(*args, **kwargs)
        self.expected = []
        return res

    def expectSystemConsole(self, exp):
        exp.sendline('\n')
        self.expect(exp, 'root@turris:/#')

    def expectLastRetval(self, exp, retval):
        exp.sendline('echo "###$?###"')
        self.expect(exp, '###%d###' % retval)
