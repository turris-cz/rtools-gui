"Module implementing steps for A module"
import sys
import pexpect
from datetime import datetime
from .generic import Step
from .exceptions import FatalWorkflowException
from .. import report
from ..moxtester.exceptions import MoxTesterImagerNoBootPrompt


class OTPProgramming(Step):
    "Program OTP memory"

    def run(self):
        if self.conf.no_otp:
            return  # Do nothing for untrusted run
        imager = self.moxtester.mox_imager(
            self.resources, self.serial_number, self.db_board.mac_wan(),
            self.db_board.revision())
        failed = False
        try:
            imager.run(self.set_progress)
        except MoxTesterImagerNoBootPrompt:
            failed = True
        recorded = self.db_board.core_info()
        if recorded is not None:
            if not failed and (recorded['mem'] != imager.ram or recorded['key'] != imager.public_key):
                return "DB value does not match:\nRam: {} : {}\nKey: {} : {}".format(
                    recorded['mem'], imager.ram, recorded['key'], imager.key)
            return None
        if failed:
            raise FatalWorkflowException("OTP programming failed")
        self.db_board.set_core_info(imager.ram, imager.public_key)
        return None

    @staticmethod
    def name():
        return "Programování OTP"

    @staticmethod
    def id():
        return "otp-program"


class SPIFlashStep(Step):
    "Generic SPI Flash programming step"

    def _flash(self, binary, address):
        self.set_progress(0)
        with self.moxtester.spiflash() as flash:
            flash.reset_device()
            flash.write(address, binary, lambda v: self.set_progress(.8 * v))
            if not flash.verify(address, binary, lambda v: self.set_progress(.8 + (.2 * v))):
                raise FatalWorkflowException("SPI content verification failed")


class ProgramSecureFirmware(SPIFlashStep):
    "Program secure firmware to SPI flash memory"

    def run(self):
        self._flash(self.resources.secure_firmware, 0x0)

    @staticmethod
    def name():
        return "Programování bezpečnostního firmwaru"

    @staticmethod
    def id():
        return "flash-secure-firmware"


class ProgramUBoot(SPIFlashStep):
    "Program u-boot to SPI flash memory"

    def run(self):
        self._flash(self.resources.uboot, 0x20000)

    @staticmethod
    def name():
        return "Programování U-Bootu"

    @staticmethod
    def id():
        return "flash-uboot"


class ProgramRescue(SPIFlashStep):
    "Program rescue to SPI flash memory"

    def run(self):
        self._flash(self.resources.rescue, 0x190000)

    @staticmethod
    def name():
        return "Programování záchranného systému"

    @staticmethod
    def id():
        return "flash-rescue"


class ProgramDTB(SPIFlashStep):
    "Program DTB to SPI flash memory"

    def run(self):
        self._flash(self.resources.dtb, 0x7f0000)

    @staticmethod
    def name():
        return "Programování DTB"

    @staticmethod
    def id():
        return "flash-dtb"


class TestBootUp(Step):
    "Try to boot Mox to u-boot"

    def run(self):
        self.set_progress(0)
        self.moxtester.power(True)
        uart = self.moxtester.uart()
        self.moxtester.reset(False)
        self.set_progress(.1)
        uart.expect(['U-Boot'])
        self.set_progress(.3)
        uart.expect(['Hit any key to stop autoboot'])
        self.set_progress(.9)
        uart.sendline('')
        uart.expect(['=>'])
        self.set_progress(1)

    @staticmethod
    def name():
        return "Test bootu Moxe"

    @staticmethod
    def id():
        return "bootup"


class UbootSaveenv(Step):
    "Save default enviroment to nor"

    def run(self):
        self.set_progress(0)
        uart = self.moxtester.uart()
        uart.sendline('env default -f -a')
        self.set_progress(.1)
        uart.expect(['=>'])
        self.set_progress(.4)
        uart.sendline('saveenv')
        self.set_progress(.5)
        uart.expect(['OK'])
        self.set_progress(.9)
        uart.expect(['=>'])
        self.set_progress(1)

    @staticmethod
    def name():
        return "Uložení výchozí konfigurace U-Bootu"

    @staticmethod
    def id():
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
        uart = self.moxtester.uart()
        now = datetime.utcnow()
        date = "{:02}{:02}{:02}{:02}{:04}.{:02}".format(
            now.month, now.day, now.hour,
            now.minute, now.year, now.second
        )
        uart.sendline('date ' + date)
        self.set_progress(.4)
        uart.expect(['=>'])
        self.set_progress(.5)
        uart.sendline('date')
        # Note: we check only date. It is not exactly safe to check for
        # time as that might change. Let's hope that in factory no one is
        # going to work over midnight.
        uart.expect(['Date: (\\d+)-(\\d+)-(\\d+)'])
        if not self._match_date(uart, now):
            raise FatalWorkflowException("Přečtené datum neodpovídá")
        uart.expect(['=>'])
        self.set_progress(1)

    @staticmethod
    def name():
        return "Nastavení aktuálního času"

    @staticmethod
    def id():
        return "datetime"


class TestUSB(Step):
    "Test USB"

    def run(self):
        self.set_progress(0)
        uart = self.moxtester.uart()
        uart.sendline('gpio set GPIO20')
        self.set_progress(.2)
        uart.expect(['=>'])
        uart.sendline('usb start')
        self.set_progress(.5)
        uart.expect(['=>'])
        self.set_progress(.6)
        uart.sendline('usb dev')
        self.set_progress(.7)
        value = uart.expect(['IDE device 0: ', 'no usb devices available'])
        if value != 0:
            raise FatalWorkflowException('USB device was not found')
        self.set_progress(1)

    @staticmethod
    def name():
        return "Test USB"

    @staticmethod
    def id():
        return "test-usb"


class TestWan(Step):
    "Test Wan"

    def _test_dhcp(self, uart):
        uart.sendline('dhcp')
        self.set_progress(.2)
        uart.expect(['Waiting for PHY auto negotiation to complete'])
        self.set_progress(.4)
        uart.expect(['DHCP client bound to address 192.168.'])
        self.set_progress(.8)

    def run(self):
        self.set_progress(0)
        uart = self.moxtester.uart()
        try:
            self._test_dhcp(uart)
        except pexpect.exceptions.TIMEOUT:
            report.log("DHCP failed. Trying again.")
            self._test_dhcp(uart)
        uart.expect(['=>'])
        uart.sendline('mii info')
        uart.expect(['PHY 0x01:'])
        uart.expect(['=>'])
        self.set_progress(1)

    @staticmethod
    def name():
        return "Test WAN"

    @staticmethod
    def id():
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
