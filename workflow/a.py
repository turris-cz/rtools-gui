"Module implementing steps for A module"
from datetime import datetime
from .generic import Step
from .exceptions import FatalWorkflowException
from time import sleep


class OTPProgramming(Step):
    "Program OTP memory"

    def run(self):
        # TODO
        pass

    @staticmethod
    def name():
        return "Programování OTP"

    @staticmethod
    def description():
        return """Programování odpovídajících údajů do jednorázově
        zapisovatelné paměti."""


class SPIFlashStep(Step):
    "Generic SPI Flash programming step"

    def _flash(self, fpath, address):
        self.set_progress(0)
        with self.moxtester.spiflash() as flash:
            flash.reset_device()
            with open(fpath, 'rb') as file:
                data = file.read()
                flash.write(address, data, lambda v: self.set_progress(int(v*80)))
                if not flash.verify(address, data, lambda v: self.set_progress(80 + int(v*20))):
                    raise FatalWorkflowException("SPI content verification failed")


class ProgramSecureFirmware(SPIFlashStep):
    "Program secure firmware to SPI flash memory"

    def run(self):
        self._flash('firmware/secure-firmware', 0x0)

    @staticmethod
    def name():
        return "Programování bezpečnostního firmwaru"

    @staticmethod
    def description():
        return """Programování bezpečnostního firmwaru do SPI Flash paměti."""


class ProgramUBoot(SPIFlashStep):
    "Program u-boot to SPI flash memory"

    def run(self):
        self._flash('firmware/u-boot', 0x20000)

    @staticmethod
    def name():
        return "Programování U-Bootu"

    @staticmethod
    def description():
        return """Programování bootloaderu U-Boot do SPI Flash paměti."""


class ProgramRescue(SPIFlashStep):
    "Program rescue to SPI flash memory"

    def run(self):
        self._flash('firmware/image.fit.lzma', 0x190000)

    @staticmethod
    def name():
        return "Programování záchraného systému"

    @staticmethod
    def description():
        return """Programování záchraného systému do SPI Flash paměti."""


class ProgramDTB(SPIFlashStep):
    "Program DTB to SPI flash memory"

    def run(self):
        self._flash('firmware/dtb', 0x7f0000)

    @staticmethod
    def name():
        return "Programování DTB"

    @staticmethod
    def description():
        return """Programování DTB do SPI Flash paměti."""


class TestBootUp(Step):
    "Try to boot Mox to u-boot"

    def run(self):
        self.set_progress(0)
        self.moxtester.power(True)
        with self.moxtester.uart() as uart:
            self.moxtester.reset(False)
            self.set_progress(40)
            uart.expect(['Hit any key to stop autoboot'])
            self.set_progress(90)
            uart.sendline('')
            uart.expect(['=>'])
            self.set_progress(100)

    @staticmethod
    def name():
        return "Test bootu Moxe"

    @staticmethod
    def description():
        return """Otestování, že MOX nabootuje bootloader (u-boot)"""


class TimeSetup(Step):
    "Set current time and verify this setting"

    def run(self):
        self.set_progress(0)
        with self.moxtester.uart() as uart:
            now = datetime.utcnow()
            date = "{:02}{:02}{:02}{:02}{:04}.{:02}".format(
                now.month, now.day, now.hour,
                now.minute, now.year, now.second
                )
            uart.sendline('date ' + date)
            self.set_progress(40)
            uart.expect(['=>'])
            self.set_progress(50)
            uart.sendline('date')
            #uart.expect(['^Date: '])
            #print(uart.before)
        self.set_progress(100)

    @staticmethod
    def name():
        return "Nastavení aktuálního času"

    @staticmethod
    def description():
        return """Nastavení a kontrola času v RTC."""


class TestUSB(Step):
    "Test USB"

    def run(self):
        self.set_progress(0)
        with self.moxtester.uart() as uart:
            uart.sendline('gpio set GPIO20')
            self.set_progress(20)
            uart.expect(['=>'])
            uart.sendline('usb start')
            self.set_progress(50)
            uart.expect(['=>'])
            self.set_progress(60)
            uart.sendline('usb dev')
            self.set_progress(70)
            value = uart.expect(['IDE device 0: ', 'no usb devices available'])
            if value != 1:
                FatalWorkflowException('USB device was not found')
        self.set_progress(100)

    @staticmethod
    def name():
        return "Test USB"

    @staticmethod
    def description():
        return """Otestování USB Moxe."""


class TestWan(Step):
    "Test Wan"

    def run(self):
        # TODO
        pass

    @staticmethod
    def name():
        return "Test WAN"

    @staticmethod
    def description():
        return """Otestování WAN Moxe."""


# All steps for MOX A in order
ASTEPS = (
    OTPProgramming,
    ProgramSecureFirmware,
    ProgramUBoot,
    ProgramRescue,
    ProgramDTB,
    TestBootUp,
    TimeSetup,
    TestUSB,
    TestWan,
)
