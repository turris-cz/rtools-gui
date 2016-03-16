import pexpect
import sys
import os

from PyQt5 import QtCore

from workflow.base import Base, BaseWorker
from application import settings


class Sample(Base):

    def __init__(self, name):
        self._name = name

    def getWorker(self):
        return SampleWorker(settings.STEP_SETTINGS['sample']['script_path'])

class SampleWorker(BaseWorker):
    def __init__(self, path):
        super(SampleWorker, self).__init__()
        self.path = path

    @QtCore.pyqtSlot()
    def start(self):
        child = pexpect.spawn(self.path, logfile=sys.stdout)
        child.expect("Phase 1")
        self.progress.emit(1)
        child.expect("Phase 2")
        self.progress.emit(20)
        child.expect("Phase 3")
        self.progress.emit(20)
        child.expect(pexpect.EOF)
        self.finished.emit(True)

class SerialReboot(Base):
    _name = "SERIAL REBOOT"

    def getWorker(self):
        return SerialRebootWorker(settings.SERIAL_CONSOLE_SETTINGS)


class SerialRebootWorker(BaseWorker):

    def __init__(self, scSettings):
        super(SerialRebootWorker, self).__init__()
        self.scSettings = scSettings

    @QtCore.pyqtSlot()
    def start(self):
        # TODO logging
        with open('/tmp/output.txt', 'w') as log_file:

            wrapper_path = os.path.join(sys.path[0], 'sc_wrapper.py')
            exp = pexpect.spawn(
                wrapper_path,
                ['-b', str(self.scSettings['baudrate']), '-d', self.scSettings['device']],
                logfile=log_file
            )
            exp.sendline('\n')
            exp.expect('root@turris:/#')
            exp.sendline('reboot')
            self.progress.emit(5)
            plan = [
                'Router Turris successfully started.',
                'fuse init',
                'procd: - init -',
                'ncompressing Kernel Image ... OK',
                'BOOT NAND',
            ]
            while True:
                res = exp.expect(plan)
                if res == 0:  # first is a final success
                    break
                else:
                    self.progress.emit(20)
                    # remove from plan (avoid going in boot cyrcles)
                    del plan[res]

            exp.terminate()

        self.finished.emit(True)


WORKFLOW = (
    Sample("POWER"),
    Sample("ATSHA"),
    Sample("UBOOT"),
    Sample("REBOOT"),
    Sample("REFLASH"),
    Sample("RTC"),
    SerialReboot(),
)
