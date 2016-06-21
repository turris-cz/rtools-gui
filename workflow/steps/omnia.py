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


class PowerTest(Base):
    _name = "POWER TEST"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            self.expectTesterConsoleInit(expTester)
            self.progress.emit(0)

            # Reset the tester
            self.expectReinitTester(expTester)
            self.progress.emit(33)

            # Perform tests
            self.expectTester(expTester, "PWRUPTEST", 33, 66)
            self.expectTester(expTester, "PWRDOWNTEST", 66, 99)

            self.progress.emit(100)
            return True


class RsvTest(Base):
    _name = "RSV TEST"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            self.expectTesterConsoleInit(expTester)
            self.progress.emit(0)

            # Reset the tester
            self.expectReinitTester(expTester)
            self.progress.emit(25)

            # Start start omnia
            self.expectTester(expTester, "HWSTART", 25, 50)
            # RSV test
            self.expectTester(expTester, "RSV", 50, 75)

            # Reset the tester
            self.expectReinitTester(expTester)
            self.progress.emit(100)
            return True


class Mcu(Base):
    _name = "MCU"

    def createWorker(self):
        return self.Worker(
            settings.PATHS['openocd_bin']['path'],
            settings.PATHS['openocd_scripts']['path'],
            settings.PATHS['openocd_config']['path'],
            settings.PATHS['bootloader_mcu']['path'],
            settings.PATHS['omnia_hw_ctrl']['path'],
        )

    class Worker(BaseWorker):

        def __init__(self, path_bin, path_scripts, path_config, path_bootloader, path_hw_ctrl):
            super(Mcu.Worker, self).__init__()
            self.command = \
                "sudo %s -s %s -f %s -f target/stm32f0x.cfg -c 'init' -c 'sleep 200' " \
                "-c 'reset halt' -c 'sleep 100' -c 'wait_halt 2' " \
                "-c 'flash write_image erase %s 0x08000000' " \
                "-c 'flash write_image erase %s 0x08005000' " \
                "-c 'sleep 100' -c 'reset run' -c 'shutdown'" \
                % (path_bin, path_scripts, path_config, path_bootloader, path_hw_ctrl)

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            self.expectTesterConsoleInit(expTester)
            self.progress.emit(0)

            # Reset the tester
            self.expectReinitTester(expTester)
            self.progress.emit(25)

            # Start programming mode
            self.expectTester(expTester, "PROGRAM", 25, 50)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')
            # Run the mcu programming script
            expLocal = self.expectStartLocalCommand(self.command)
            self.progress.emit(75)

            # TODO progress
            self.expect(expLocal, pexpect.EOF)
            self.testExitStatus(expLocal)

            self.progress.emit(100)

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
            self.expectTesterConsoleInit(expTester)
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
            self.expectTesterConsoleInit(expTester)
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
    PowerTest(),
    Mcu(),
    #Uboot(),
    #Atsha(),
    #Sample("REBOOT"),
    #Sample("REFLASH"),
    #Sample("RTC"),
    #UbootCommands("UBOOT X", ["boot"], True),
    #SerialReboot(),
    RsvTest(),
)
