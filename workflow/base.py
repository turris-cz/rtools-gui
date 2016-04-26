import abc
import os
import pexpect
import sys
import time

from PyQt5 import QtCore


class PrefixFile(file):
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.get('prefix', "")
        kwargs.pop("prefix", None)
        super(PrefixFile, self).__init__(*args, **kwargs)

    def write(self, string, *args, **kwargs):
        res = string.replace("\n", "\n%s> " % self.prefix)
        return super(PrefixFile, self).write(res, *args, **kwargs)

    def writelines(self, stringSeq, *args, **kwargs):
        res = []
        for e in stringSeq:
            res.append(e.replace("\n", "\n%s> " % self.prefix))

        return super(PrefixFile, self).writelines(res, *args, **kwargs)


def spawnPexpectSerialConsole(device):
    return pexpect.spawn(os.path.join(sys.path[0], 'sc_connector.py'), ["-d", device])


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

        # Open log
        with open(self.logfile, 'a') as self.log, \
                PrefixFile(self.logfile, "a", prefix="local") as self.logLocal:

            # Write header
            self.log.write("\n########## %s ##########\n" % self.name)
            self.log.flush()

            error_msg = ""
            try:
                retval = self.perform()
            except pexpect.TIMEOUT:
                error_msg = "\n>>>>>>>>>> TIMEOUT \"%s\" <<<<<<<<<<\n" % str(self.expected)
                retval = False
            except Exception as e:
                error_msg = "\n>>>>>>>>>> ERROR \"%s\" <<<<<<<<<<\n" % e.message
                retval = False
            finally:
                self.logLocal.flush()

            # Wait for some time before the console output is flushed
            time.sleep(0.3)

            # Write the tail
            if retval:
                self.log.write("\n---------- %s ----------\n" % self.name)
            else:
                self.log.write(error_msg)
                self.log.write("\n!!!!!!!!!! %s !!!!!!!!!!\n" % self.name)
            self.log.flush()

        self.finished.emit(True if retval else False)  # Boolean needs to be emitted

    def expectCommand(self, exp, cmd):
        """ perform local command"""
        exp.sendline(cmd)
        self.expectLastRetval(exp, 0)

    def expectLocalCommand(self, cmd):
        """ perform local command"""
        exp = pexpect.spawn("sh", logfile=self.logLocal)
        exp.sendline(cmd)
        self.expectLastRetval(exp, 0)
        exp.terminate(force=True)

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
