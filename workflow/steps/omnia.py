import pexpect
import sys
import os

from workflow.base import Base, BaseWorker
from application import settings


class Sample(Base):

    def __init__(self, name):
        self._name = name

    def createWorker(self):
        return SampleWorker(settings.STEP_SETTINGS['sample']['script_path'])

class SampleWorker(BaseWorker):
    def __init__(self, scriptPath):
        super(SampleWorker, self).__init__()
        self.scriptPath = scriptPath

    def perform(self):
        exp = pexpect.spawn(self.scriptPath, logfile=self.log)
        exp.expect("Phase 1")
        self.progress.emit(1)
        exp.expect("Phase 2")
        self.progress.emit(20)
        exp.expect("Phase 3")
        self.progress.emit(20)
        exp.expect(pexpect.EOF)
        exp.terminate(force=True)
        return True

class SerialReboot(Base):
    _name = "SERIAL REBOOT"

    def createWorker(self):
        return SerialRebootWorker(settings.SERIAL_CONSOLE_SETTINGS)


class SerialRebootWorker(BaseWorker):

    def __init__(self, scSettings):
        super(SerialRebootWorker, self).__init__()
        self.scSettings = scSettings

    def perform(self):
        wrapper_path = os.path.join(sys.path[0], 'sc_wrapper.py')
        exp = pexpect.spawn(
            wrapper_path,
            ['-b', str(self.scSettings['baudrate']), '-d', self.scSettings['device']],
            logfile=self.log
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
        exp.terminate(force=True)
        return True


WORKFLOW = (
    Sample("POWER"),
    Sample("ATSHA"),
    Sample("UBOOT"),
    Sample("REBOOT"),
    Sample("REFLASH"),
    Sample("RTC"),
    SerialReboot(),
)
