"Module implementing steps for A module"
import sys
from datetime import datetime
from .generic import Step
from .exceptions import FatalWorkflowException


class OTPProgramming(Step):
    "Program OTP memory"

    def _imager_callback(self, progress):
        self.set_progress(int(100*progress))

    def run(self):
        if self.conf.no_otp:
            return  # Do nothing for untrusted run
        imager = self.moxtester.mox_imager(
            self.resources, self.serial_number, self.db_board.mac_wan(),
            self.db_board.revision())
        imager.run(self._imager_callback)
        # TODO verify serial number and others with real from imager
        self.db_board.set_core_info(imager.ram, imager.public_key)

    @staticmethod
    def name():
        return "Programování OTP"

    @staticmethod
    def dbid():
        return "otp-program"


class SPIFlashStep(Step):
    "Generic SPI Flash programming step"

    def _flash(self, binary, address):
        self.set_progress(0)
        with self.moxtester.spiflash() as flash:
            flash.reset_device()
            flash.write(address, binary, lambda v: self.set_progress(int(v*80)))
            if not flash.verify(address, binary, lambda v: self.set_progress(80 + int(v*20))):
                raise FatalWorkflowException("SPI content verification failed")


class ProgramSecureFirmware(SPIFlashStep):
    "Program secure firmware to SPI flash memory"

    def run(self):
        self._flash(self.resources.secure_firmware, 0x0)

    @staticmethod
    def name():
        return "Programování bezpečnostního firmwaru"

    @staticmethod
    def dbid():
        return "flash-secure-firmware"


class ProgramUBoot(SPIFlashStep):
    "Program u-boot to SPI flash memory"

    def run(self):
        self._flash(self.resources.uboot, 0x20000)

    @staticmethod
    def name():
        return "Programování U-Bootu"

    @staticmethod
    def dbid():
        return "flash-uboot"


class ProgramRescue(SPIFlashStep):
    "Program rescue to SPI flash memory"

    def run(self):
        self._flash(self.resources.rescue, 0x190000)

    @staticmethod
    def name():
        return "Programování záchranného systému"

    @staticmethod
    def dbid():
        return "flash-rescue"


class ProgramDTB(SPIFlashStep):
    "Program DTB to SPI flash memory"

    def run(self):
        self._flash(self.resources.dtb, 0x7f0000)

    @staticmethod
    def name():
        return "Programování DTB"

    @staticmethod
    def dbid():
        return "flash-dtb"


class TestBootUp(Step):
    "Try to boot Mox to u-boot"

    def run(self):
        self.set_progress(0)
        self.moxtester.power(True)
        with self.moxtester.uart() as uart:
            self.moxtester.reset(False)
            self.set_progress(10)
            uart.expect(['U-Boot'])
            self.set_progress(30)
            uart.expect(['Hit any key to stop autoboot'])
            self.set_progress(90)
            uart.sendline('')
            uart.expect(['=>'])
            self.set_progress(100)

    @staticmethod
    def name():
        return "Test bootu Moxe"

    @staticmethod
    def dbid():
        return "bootup"


class UbootSaveenv(Step):
    "Save default enviroment to nor"

    def run(self):
        self.set_progress(0)
        with self.moxtester.uart() as uart:
            uart.sendline('saveenv')
            self.set_progress(10)
            uart.expect(['OK'])
            self.set_progress(90)
            uart.expect(['=>'])
        self.set_progress(100)

    @staticmethod
    def name():
        return "Uložení výchozí konfigurace U-Bootu"

    @staticmethod
    def dbid():
        return "uboot-saveenv"


class TimeSetup(Step):
    "Set current time and verify this setting"

    @staticmethod
    def _match_date(uart, now):
        def _group2int(group):
            return int(uart.match.group(group).decode(sys.getdefaultencoding()))
        return \
            now.year == _group2int(1) and \
            now.month == _group2int(2) and \
            now.day == _group2int(3)

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
            # Note: we check only date. It is not exactly safe to check for
            # time as that might change. Let's hope that in factory no one is
            # going to work over midnight.
            uart.expect(['Date: (\d+)-(\d+)-(\d+)'])
            if not self._match_date(uart, now):
                raise FatalWorkflowException("Přečtené datum neodpovídá")
            uart.expect(['=>'])
        self.set_progress(100)

    @staticmethod
    def name():
        return "Nastavení aktuálního času"

    @staticmethod
    def dbid():
        return "datetime"


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
            if value != 0:
                FatalWorkflowException('USB device was not found')
        self.set_progress(100)

    @staticmethod
    def name():
        return "Test USB"

    @staticmethod
    def dbid():
        return "test-usb"


class TestWan(Step):
    "Test Wan"

    def run(self):
        self.set_progress(0)
        with self.moxtester.uart() as uart:
            uart.sendline('dhcp')
            self.set_progress(20)
            uart.expect(['Waiting for PHY auto negotiation to complete'])
            self.set_progress(40)
            uart.expect(['DHCP client bound to address 192.168.'])
            self.set_progress(80)
            uart.expect(['=>'])
        self.set_progress(100)

    @staticmethod
    def name():
        return "Test WAN"

    @staticmethod
    def dbid():
        return "test-wan"


# All steps for MOX A in order
ASTEPS = (
    OTPProgramming,
    ProgramSecureFirmware,
    ProgramUBoot,
    ProgramRescue,
    ProgramDTB,
    TestBootUp,
    UbootSaveenv,
    TimeSetup,
    TestUSB,
    TestWan,
)
