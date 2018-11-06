"Module implementing steps for A module"
from datetime import datetime
from .generic import Step
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


class SPIProgramming(Step):
    "Program SPI Flash memory"

    def run(self):
        # TODO
        pass

    @staticmethod
    def name():
        return "Programování SPI Flash paměti"

    @staticmethod
    def description():
        return """Programování bezpečnostního firmwaru, bootloaderu (u-boot) a
        záchranného image do SPI Flash paměti. Tento krok také provádí
        kontrolu."""


class TestBootUp(Step):
    "Try to boot Mox to u-boot"

    def run(self):
        self.moxtester.power(True)
        with self.moxtester.uart() as uart:
            self.moxtester.reset(False)
            self.set_progress(40)
            uart.expect(['Hit any key to stop autoboot'])
            self.set_progress(90)
            uart.send('\n')
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
        with self.moxtester.uart() as uart:
            now = datetime.utcnow()
            date = "{:02}{:02}{:02}{:02}{:04}.{:02}".format(
                now.month, now.day, now.hour,
                now.minute, now.year, now.second
                )
            uart.send('date ' + date)
            uart.expect(['=>'])
            # TODO verify date

    @staticmethod
    def name():
        return "Nastavení aktuálního času"

    @staticmethod
    def description():
        return """Nastavení a kontrola času v RTC."""


class PeripheryTest(Step):
    "Test USB, Wan and so on"

    def run(self):
        # TODO
        pass

    @staticmethod
    def name():
        return "Test periferií"

    @staticmethod
    def description():
        return """Otestování periferií Moxe."""


# All steps for MOX A in order
ASTEPS = (
    OTPProgramming,
    SPIProgramming,
    TestBootUp,
    TimeSetup,
    PeripheryTest,
)
