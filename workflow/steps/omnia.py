import pexpect
import time
import datetime
import binascii
import struct

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
            self.progress.emit(25)

            # Put CPU in reset
            self.expectTester(expTester, "CPUOFF", 25, 50)
            # Switch off MCU
            self.expectTester(expTester, "MCUOFF", 50, 75)

            # Perform tests
            self.expectTester(expTester, "PWRUPTEST", 75, 99)
            #self.expectTester(expTester, "PWRDOWNTEST", 66, 99)

            self.progress.emit(100)
            return True


class RsvTest(Base):
    _name = "RSV TEST"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            expRouter = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.expectTesterConsoleInit(expTester)
            self.progress.emit(0)

            # Reset the tester
            self.expectReinitTester(expTester)
            self.progress.emit(10)

            # Start start omnia
            self.expectTester(expTester, "HWSTART", 10, 20)

            # Wait till board is booted
            self.expectWaitBooted(expRouter, 20, 80)

            # RSV test
            self.expectTester(expTester, "RSV", 80, 90)

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
    _name = "SPI UBOOT"

    def createWorker(self):
        return self.Worker(
            settings.PATHS['flashrom']['path'],
            settings.PATHS['uboot_image']['path'],
            settings.SPI_SPEED,
        )

    class Worker(BaseWorker):

        def __init__(self, path_flashrom, path_image, spi_speed):
            super(Uboot.Worker, self).__init__()
            self.flash_image_command = \
                "sudo %s -p linux_spi:dev=/dev/spidev0.0,spispeed=%d -w %s" \
                % (path_flashrom, spi_speed, path_image)

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            self.progress.emit(0)

            self.expectTesterConsoleInit(expTester)
            self.progress.emit(5)
            self.expectReinitTester(expTester)
            self.progress.emit(10)

            # Start programming mode
            self.expectTester(expTester, "PROGRAM", 10, 20)

            # Put CPU in reset
            self.expectTester(expTester, "CPUOFF", 20, 30)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')

            # Prepare SPI
            self.expectLocalCommand("gpio export 21 out")
            self.progress.emit(40)
            self.expectLocalCommand("gpio mode 21 out")
            self.progress.emit(45)
            self.expectLocalCommand("gpio write 21 0")
            self.progress.emit(50)

            # Flash uboot image
            expLocal = self.expectStartLocalCommand(self.flash_image_command, 90)
            while True:
                res = self.expect(expLocal, [
                    pexpect.EOF,
                    r'Calibrating delay loop...',
                    r'Reading old flash chip contents...',
                    r'Erasing and writing flash chip...',
                    r'Verifying flash...',
                ])
                if res == 0:
                    break
                self.progress.emit(50 + 10 * res)
            self.testExitStatus(expLocal)
            self.progress.emit(95)

            # Deactivate SPI
            self.expectLocalCommand("gpio write 21 1")
            self.progress.emit(100)

            expTester.terminate(force=True)
            return True


class Atsha(Base):
    _name = "ATSHA"

    def createWorker(self):
        return self.Worker(settings.PATHS['atsha']['path'], qApp.router.id)

    class Worker(BaseWorker):

        def __init__(self, scriptPath, serial):
            super(Atsha.Worker, self).__init__()
            self.flashAtshaCmd = "%s %s" % (scriptPath, serial)

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            self.progress.emit(0)

            self.expectTesterConsoleInit(expTester)
            self.progress.emit(10)
            self.expectReinitTester(expTester)
            self.progress.emit(20)

            # Start programming mode
            self.expectTester(expTester, "PROGRAM", 20, 35)

            # Put CPU in reset
            self.expectTester(expTester, "CPUOFF", 35, 50)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')

            # Run the atsha programming script
            expLocal = self.expectStartLocalCommand(self.flashAtshaCmd, 90)
            while True:
                res = self.expect(expLocal, [
                    pexpect.EOF,
                    r'ATSHA204 programming...',
                    r'ATSHA204 test...',
                ])
                if res == 0:
                    break
                self.progress.emit(50 + 20 * res)
            self.testExitStatus(expLocal)
            self.progress.emit(100)

            expTester.terminate(force=True)
            return True


class EepromFlash(Base):
    _name = "EEPROM FLASH"

    def createWorker(self):
        return self.Worker(settings.ROUTER_RAMSIZE, settings.REGION)

    class Worker(BaseWorker):

        def __init__(self, ramsize, region=None):
            super(EepromFlash.Worker, self).__init__()
            # The only two valid options are `1` or `2`
            self.ramsize = ramsize
            self.region = region

        @staticmethod
        def makeImage(ramsize, region=None):
            magic = 0x0341a034
            region = int(binascii.hexlify(region), 16) if region else 0x0000
            data = struct.pack('III', magic, ramsize, region)
            # add crc
            data = struct.pack('IIII', magic, ramsize, region, binascii.crc32(data) % (1 << 32))
            return data

        def perform(self):

            if self.ramsize not in (1, 2, ):
                raise ValueError("Ramsize could be only '1' or '2' (%d given)" % self.ramsize)

            if self.region is not None and len(self.region) != 2:
                raise ValueError("Incorrect region (%s given)" % self.region)

            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            self.progress.emit(0)

            self.expectTesterConsoleInit(expTester)
            self.progress.emit(10)
            self.expectReinitTester(expTester)
            self.progress.emit(20)

            # Start programming mode
            self.expectTester(expTester, "PROGRAM", 20, 30)

            # Put CPU in reset
            self.expectTester(expTester, "CPUOFF", 30, 40)

            # Add \n into local console to split tester and local output
            self.logLocal.write('\n')

            self.expectLocalCommand("i2cset -y 1 0x70 0 2 b")
            self.progress.emit(50)

            # try to set i2c into a initial state (this can fail)
            expLocal = self.expectStartLocalCommand(
                "sudo bash -c 'echo 0x54 > /sys/class/i2c-adapter/i2c-1/delete_device'")
            self.expect(expLocal, pexpect.EOF)
            self.progress.emit(60)

            self.expectLocalCommand(
                "sudo bash -c 'echo 24c64 0x54 > /sys/class/i2c-adapter/i2c-1/new_device'")
            self.progress.emit(70)

            image = self.makeImage(self.ramsize, self.region)
            devicePath = '/sys/devices/platform/soc/3f804000.i2c/i2c-1/1-0054/eeprom'
            self.expectLocalCommand(
                'sudo bash -c "echo -n -e %s > %s"' % (repr(image), devicePath))
            self.progress.emit(80)

            # cleanup
            self.expectLocalCommand(
                "sudo bash -c 'echo 0x54 > /sys/class/i2c-adapter/i2c-1/delete_device'")
            self.progress.emit(90)

            self.ram.emit(self.ramsize, 'S')
            self.progress.emit(100)

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

    def __init__(self, name, cmds, bootPlan=None):
        self._name = name
        self.cmds = cmds
        self.bootPlan = bootPlan

    def createWorker(self):
        return self.Worker(self.name, self.cmds, self.bootPlan)

    class Worker(BaseWorker):
        def __init__(self, name, cmds, bootPlan):
            super(UbootCommands.Worker, self).__init__()
            self.name = name
            self.cmds = cmds
            self.bootPlan = bootPlan

        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            expRouter = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(0)

            self.expectTesterConsoleInit(expTester)
            self.progress.emit(5)
            self.expectReinitTester(expTester)
            self.progress.emit(10)

            # reset using tester
            self.expectTester(expTester, "RESETDUT", 10, 15)

            # get into uboot shell
            # unfortunatelly can't wait for "Hit any key to stop autoboot" msg (too small delay)
            # so a several new line commands will be sent there

            tries = 10  # 10s shall be enough
            while True:
                time.sleep(1)
                expRouter.sendline('\n')
                res = self.expect(expRouter, [r'.*[\n\r]+=>.*', r'.+'] if tries > 0 else r'=>')
                if res == 0:
                    break
                else:
                    tries -= 1
            self.progress.emit(20)

            # perform commands
            cmds_progress = 80 if self.bootPlan is False else 30
            for i in range(len(self.cmds)):
                expRouter.sendline(self.cmds[i])
                self.progress.emit(20 + (i + 1) * cmds_progress / len(self.cmds))
                # wait for some time just to be sure
                time.sleep(0.1)

            # if boot plan is False continue otherwise wait for booted
            if self.bootPlan is not False:
                self.expectWaitBooted(expRouter, timeout=150, plan=self.bootPlan)
            self.progress.emit(100)

            return True


class ClockSet(Base):
    _name = "CLOCK SET"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):
        def perform(self):
            expTester = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
            expRouter = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(0)

            self.expectTesterConsoleInit(expTester)
            self.progress.emit(5)
            self.expectReinitTester(expTester)
            self.progress.emit(10)

            # reset using tester
            self.expectTester(expTester, "RESETDUT", 10, 15)
            self.expectWaitBooted(expRouter, 15, 80)
            self.expectSystemConsole(expRouter)
            self.progress.emit(85)
            now = datetime.datetime.utcnow()
            expRouter.sendline("date -u -s '%04d-%02d-%02d %02d:%02d:%02d'" % (
                now.year, now.month, now.day, now.hour, now.minute, now.second
            ))
            self.expectLastRetval(expRouter, 0)
            self.progress.emit(90)

            # Calling hwclock only once sometimes fails to set the clock and no error is
            # displayed
            # calling it twice sets the clock every time...
            expRouter.sendline("hwclock -u -w")
            self.expectLastRetval(expRouter, 0)
            self.progress.emit(95)
            expRouter.sendline("hwclock -u -w")
            self.expectLastRetval(expRouter, 0)
            self.progress.emit(100)

            return True


WORKFLOW = (
    PowerTest(),
    Mcu(),
    Uboot(),
    Atsha(),
    EepromFlash(),
    UbootCommands("USB FLASHING", ["setenv rescue 3", "run rescueboot"], bootPlan=[
        ('Router Turris successfully started.', 100),
        ('Mode: Reflash...', 50),
        ('Reflash succeeded.', 75),
    ]),
    ClockSet(),
    #Sample("REBOOT"),
    #Sample("REFLASH"),
    #Sample("RTC"),
    #UbootCommands("UBOOT X", ["boot"], True),
    #SerialReboot(),
    RsvTest(),
)
