"Module implementing steps for A module"
from .generic import Step


class OTPProgramming(Step):
    "Program OTP memory"

    @staticmethod
    def name():
        return "Programování OTP"

    @staticmethod
    def description():
        return """Programování odpovídajících údajů do jednorázově
        zapisovatelné paměti."""

    @staticmethod
    def substeps():
        return None


class SPIProgramming(Step):
    "Program SPI Flash memory"

    @staticmethod
    def name():
        return "Programování SPI Flash paměti"

    @staticmethod
    def description():
        return """Programování bezpečnostního firmwaru, bootloaderu (u-boot) a
        záchranného image do SPI Flash paměti. Tento krok také provádí
        kontrolu."""

    @staticmethod
    def substeps():
        return None


class TestBootUp(Step):
    "Try to boot Mox to u-boot"

    @staticmethod
    def name():
        return "Test bootu Moxe"

    @staticmethod
    def description():
        return """Otestování, že MOX nabootuje bootloader (u-boot)"""

    @staticmethod
    def substeps():
        return None


class TimeSetup(Step):
    "Set current time and verify this setting"

    @staticmethod
    def name():
        return "Nastavení aktuálního času"

    @staticmethod
    def description():
        return """Nastavení a kontrola času v RTC."""

    @staticmethod
    def substeps():
        return None


class PeripheryTest(Step):
    "Test USB, Wan and so on"

    @staticmethod
    def name():
        return "Test periferií"

    @staticmethod
    def description():
        return """Otestování periferií Moxe."""

    @staticmethod
    def substeps():
        return None


# All steps for MOX A in order
ASTEPS = (
    OTPProgramming,
    SPIProgramming,
    TestBootUp,
    TimeSetup,
    PeripheryTest,
)
