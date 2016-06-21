import abc
import getpass
import os
import pexpect
import socket
import sys
import time

from PyQt5 import QtCore

from custom_exceptions import LocalCommandFailed


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

    def expectLocalCommand(self, cmd):
        exp = self.expectStartLocalCommand(cmd)
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
        self.expect(exp, '###%d###' % retval)

    def expectWaitBooted(self, exp, progressStart, progressEnd, timeout=60):
        progressDiff = progressEnd - progressStart
        plan = [
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

    def expectTesterLineBreak(self, exp):
        exp.sendline('\r\n')

    def expectTester(self, exp, cmd, progressStart, progressEnd):
        step = (progressEnd - progressStart) / 10.0  # tester prints 10 dots
        current = progressStart
        res = None
        exp.sendline(cmd + "\r\n")
        while not res:
            res = self.expect(exp, [r'\.', r'OK\r\n'])
            if res == 0:
                current += step
                self.progress.emit(current if current < progressEnd else progressEnd)

    def expectReinitTester(self, exp):
        exp.sendline("RESETALL\r\n")
        self.expect(exp, r'System ready... OK')
