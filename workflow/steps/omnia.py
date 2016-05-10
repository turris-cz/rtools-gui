import pexpect
import time

from workflow.base import Base, BaseWorker, spawnPexpectSerialConsole
from application import settings


class Sample(Base):

    def __init__(self, name):
        self._name = name

    def createWorker(self):
        return self.Worker(settings.SCRIPTS['sample']['script_path'])

    class Worker(BaseWorker):
        def __init__(self, scriptPath):
            super(Sample.Worker, self).__init__()
            self.scriptPath = scriptPath

        def perform(self):
            self.logLocal.write("\n")
            exp = pexpect.spawn(self.scriptPath, logfile=self.logLocal)
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
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.expectSystemConsole(exp)
            exp.sendline('reboot')
            self.progress.emit(5)
            self.expectWaitBooted(exp, 5, 99)
            self.progress.emit(100)
            exp.terminate(force=True)
            return True


class Tester(Base):

    def __init__(self, name, cmds):
        self._name = name
        self.cmds = cmds

    def createWorker(self):
        return self.Worker(self.name, self.cmds)

    class Worker(BaseWorker):
        def __init__(self, name, cmds):
            super(Tester.Worker, self).__init__()
            self.name = name
            self.cmds = cmds

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            exp.sendline("\n")

            progress = 0.0
            self.progress.emit(progress)

            for cmd in self.cmds:
                res = None
                cmd_progress = progress
                exp.sendline(cmd)
                while not res:
                    res = self.expect(exp, [r'\.', r'OK\r\n'])
                    if res == 0:
                        cmd_progress += 100.0 / len(self.cmds) / 10
                        self.progress.emit(cmd_progress)

                progress += 100.0 / len(self.cmds)
                self.progress.emit(progress)

            self.progress.emit(100)
            exp.terminate(force=True)
            return True


class UbootCommands(Base):

    def __init__(self, name, cmds, bootCheck=True):
        self._name = name
        self.cmds = cmds
        self.bootCheck = bootCheck

    def createWorker(self):
        return self.Worker(self.name, self.cmds, self.bootCheck)

    class Worker(BaseWorker):
        def __init__(self, name, cmds, bootCheck):
            super(UbootCommands.Worker, self).__init__()
            self.name = name
            self.cmds = cmds
            self.bootCheck = bootCheck

        def perform(self):
            # perform tester DUT
            testerExp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            routerExp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            # reset using tester
            testerExp.sendline("RESET")
            self.expect(testerExp, "OK")
            self.progress.emit(10)

            # get into uboot shell
            # unfortunatelly can't wait for "Hit any key to stop autoboot" msg (too small delay)
            # so a several new line commands will be sent there

            tries = 10  # 10s shall be enough
            while True:
                time.sleep(1)
                routerExp.sendline('\n')
                res = self.expect(routerExp, ['=>', ".+"] if tries > 0 else '=>')
                if res == 0:
                    break
                else:
                    tries -= 1
            self.progress.emit(20)

            # perform commands
            cmds_progress = 30 if self.bootCheck else 80
            for i in range(len(self.cmds)):
                routerExp.sendline(self.cmds[i])
                self.progress.emit(20 + (i + 1) * cmds_progress / len(self.cmds))

            # wait for boot if specified
            if self.bootCheck:
                self.expectWaitBooted(routerExp, 50, 100)

            return True


WORKFLOW = (
    Tester("TESTER ALL", ["PWRUP", "PROGRAM", "RSV", "PWRDOWN", "HWSTART", "RSV", "RESET"]),
    Sample("POWER"),
    Sample("ATSHA"),
    Sample("UBOOT"),
    Sample("REBOOT"),
    Sample("REFLASH"),
    Sample("RTC"),
    UbootCommands("UBOOT X", ["boot"], True),
    SerialReboot(),
)
