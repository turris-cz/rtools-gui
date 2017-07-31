import abc
import getpass
import os
import pexpect
import socket
import sys
import time

from PyQt5 import QtCore

from custom_exceptions import LocalCommandFailed, RunFailed
from utils import PrefixFile


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

    def getWorker(self, logfile, startTime):
        worker = self.createWorker()
        setattr(worker, 'name', self.name)
        setattr(worker, 'logfile', logfile)
        setattr(worker, 'startTime', startTime)
        return worker


class BaseTest(Base):
    continueOnFailure = True


class BaseWorker(QtCore.QObject):
    askUser = QtCore.pyqtSignal(str, dict, QtCore.QMutex, QtCore.QWaitCondition)
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(bool)
    firmware = QtCore.pyqtSignal(str)
    ram = QtCore.pyqtSignal(int, str)
    eeprom = QtCore.pyqtSignal(str, str)
    mcu = QtCore.pyqtSignal(str, str)
    uboot = QtCore.pyqtSignal(str)
    setTitle = QtCore.pyqtSignal(str)
    expTester = None

    @abc.abstractmethod
    def perform(self):
        pass

    @QtCore.pyqtSlot()
    def start(self):
        self.expected = []

        # Open log
        with open(self.logfile, 'a') as self.log, PrefixFile(
                self.logfile, "a", prefix="local", startTime=self.startTime) as self.logLocal:

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
        """ perform command"""
        exp.sendline("\n" + cmd)  # add \n to separate outputs in log
        self.expectLastRetval(exp, 0)

    def expectStartLocalCommand(self, cmd, timeout=30):
        """ perform local command"""
        self.logLocal.write("\n%s@%s # %s\n" % (getpass.getuser(), socket.gethostname(), cmd))
        self.logLocal.flush()
        return pexpect.spawn(
            cmd, logfile=self.logLocal, env=dict(PS1='$(whoami)@$(hostname) # '),
            timeout=timeout
        )

    def expectLocalCommand(self, cmd, timeout=30):
        exp = self.expectStartLocalCommand(cmd, timeout)
        self.expect(exp, pexpect.EOF)
        self.testExitStatus(exp)

    def testExitStatus(self, exp):
        if not exp.isalive() and exp.exitstatus != 0:
            raise LocalCommandFailed(
                "cmd '%s' failed (status=%d)" % (" ".join(exp.args), exp.exitstatus))

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
        self.expect(exp, r'###([0-9]+)###')
        try:
            result = int(exp.match.group(1))
        except ValueError:
            raise RunFailed("Failed to get the retval of a command!")

        if retval != result:
            raise RunFailed("Last command exited with %d (expected %d)!" % (result, retval))

    def expectWaitBooted(self, exp, progressStart=0, progressEnd=100, timeout=60, plan=None):
        progressDiff = progressEnd - progressStart
        plan = plan or [
            ('Router Turris successfully started.', progressStart + progressDiff),
            ('fuse init', progressStart + progressDiff * 75 / 100),
            ('procd: - init -', progressStart + progressDiff * 55 / 100),
            ('ncompressing Kernel Image ... OK', progressStart + progressDiff * 40 / 100),
            ('BOOT NAND', progressStart + progressDiff * 20 / 100),
        ]

        while True:
            res = self.expect(exp, [e[0] for e in plan], timeout=timeout)
            self.progress.emit(plan[res][1])
            if res == 0:  # first is a final success
                break
            else:
                # remove from plan (avoid going in boot cyrcles)
                del plan[res]

    def expectTesterConsoleInit(self, exp):
        exp.sendline('UNKNOWN_COMMAND')
        self.expect(exp, r'error')
        exp.sendline('\n')
        exp.sendline('\n')
        time.sleep(0.5)

    def expectTester(self, exp, cmd, progressStart, progressEnd):
        step = (progressEnd - progressStart) / 10.0  # tester prints 10 dots
        current = progressStart
        res = None
        exp.sendline(cmd)
        while not res:
            res = self.expect(exp, [r'\.', r'OK[\r\n]+'])
            if res == 0:
                current += step
                self.progress.emit(current if current < progressEnd else progressEnd)

    def expectReinitTester(self, exp):
        exp.sendline("RESETALL")
        self.expect(exp, r'System ready... OK')

    def resetAllCleanup(self):
        # Try to set resetall
        if self.expTester:
            self.expTester.sendline("\n")
            time.sleep(0.5)
            self.expTester.sendline("RESETALL")

    def waitForUserReply(self, msg):
        condition = QtCore.QWaitCondition()
        mutex = QtCore.QMutex()
        mutex.lock()
        res = {}
        self.askUser.emit(msg, res, mutex, condition)
        condition.wait(mutex)
        return res['result']
