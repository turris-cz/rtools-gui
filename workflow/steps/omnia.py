import pexpect
import time

from workflow.base import Base, BaseWorker, spawnPexpectSerialConsole
from application import qApp, settings


class Sample(Base):

    def __init__(self, name):
        self._name = name

    def createWorker(self):
        return self.Worker(settings.PATHS['sample']['path'])

    class Worker(BaseWorker):
        def __init__(self, scriptPath):
            super(Sample.Worker, self).__init__()
            self.scriptPath = scriptPath

        def perform(self):
            self.logLocal.write("\n")
            exp = self.expectStartLocalCommand(self.scriptPath)
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


class Mcu(Base):
    _name = "MCU"

    def createWorker(self):
        return self.Worker(settings.PATHS['mcu']['path'])

    class Worker(BaseWorker):

        def __init__(self, scriptPath):
            super(Mcu.Worker, self).__init__()
            self.scriptPath = scriptPath

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            expTester.sendline("\n")
            self.progress.emit(0)

            # Reset the tester
            self.expectReinitTester(expTester)
            self.progress.emit(10)

            self.expectTester(expTester, "PWRUPTEST", 10, 20)
            self.expectTester(expTester, "PROGRAM", 20, 30)

            # Turn on MCU
            self.expectTester(expTester, "MCUON", 0, 33)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')
            # Run the mcu programming script
            expLocal = self.expectStartLocalCommand(self.scriptPath)

            # TODO progress
            self.expect(expLocal, pexpect.EOF)
            self.testExitStatus(expLocal)

            self.progress.emit(66)

            # Turn off MCU
            self.expectTester(expTester, "MCUOFF", 66, 100)

            expTester.terminate(force=True)
            return True


class Uboot(Base):
    _name = "UBOOT"

    def createWorker(self):
        return self.Worker(settings.PATHS['uboot_flashing']['path'])

    class Worker(BaseWorker):

        def __init__(self, scriptPath):
            super(Uboot.Worker, self).__init__()
            self.scriptPath = scriptPath

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            expTester.sendline("\n")
            self.progress.emit(0)

            # Turn on MCU
            self.expectTester(expTester, "CPUOFF", 0, 33)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')
            # Run the uboot flashing script
            expLocal = self.expectStartLocalCommand(self.scriptPath)

            # TODO progress
            self.expect(expLocal, pexpect.EOF)
            self.testExitStatus(expLocal)

            self.progress.emit(66)

            # Turn off MCU
            self.expectTester(expTester, "CPUON", 66, 100)

            expTester.terminate(force=True)
            return True


class Atsha(Base):
    _name = "ATSHA"

    def createWorker(self):
        return self.Worker(settings.PATHS['atsha']['path'], qApp.router.idHex)

    class Worker(BaseWorker):

        def __init__(self, scriptPath, serial):
            super(Atsha.Worker, self).__init__()
            self.scriptPath = scriptPath
            self.serial = serial

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            expTester.sendline("\n")
            self.progress.emit(0)

            # Turn on MCU
            self.expectTester(expTester, "CPUOFF", 0, 33)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')
            # Run the atsha programming script
            expLocal = self.expectStartLocalCommand('%s %s' % (self.scriptPath, self.serial))

            # TODO progress
            self.expect(expLocal, pexpect.EOF)
            self.testExitStatus(expLocal)

            self.progress.emit(66)

            # Turn off MCU
            self.expectTester(expTester, "CPUON", 66, 100)

            expTester.terminate(force=True)
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
            self.expectTester(testerExp, "RESETDUT", 1, 10)
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
    Mcu(),
    Uboot(),
    Atsha(),
    Sample("REBOOT"),
    Sample("REFLASH"),
    Sample("RTC"),
    UbootCommands("UBOOT X", ["boot"], True),
    SerialReboot(),
)
