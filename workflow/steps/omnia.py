import pexpect

from workflow.base import Base, BaseWorker, spawnPexpectSerialConsole
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
        self.progress.emit(2)
        self.expect(exp, "Phase 1")
        self.progress.emit(34)
        self.expect(exp, "Phase 2")
        self.progress.emit(66)
        self.expect(exp, "Phase 3")
        self.progress.emit(98)
        self.expect(exp, pexpect.EOF)
        self.progress.emit(100)
        exp.terminate(force=True)
        return True

class SerialReboot(Base):
    _name = "SERIAL REBOOT"

    def createWorker(self):
        return SerialRebootWorker()


class SerialRebootWorker(BaseWorker):

    def perform(self):
        exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
        self.expectSystemConsole(exp)
        exp.sendline('reboot')
        self.progress.emit(5)
        plan = [
            ('Router Turris successfully started.', 99),
            ('fuse init', 75),
            ('procd: - init -', 55),
            ('ncompressing Kernel Image ... OK', 40),
            ('BOOT NAND', 20),
        ]
        while True:
            res = self.expect(exp, [e[0] for e in plan])
            self.progress.emit(plan[res][1])
            if res == 0:  # first is a final success
                break
            else:
                # remove from plan (avoid going in boot cyrcles)
                del plan[res]

        self.progress.emit(100)
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
