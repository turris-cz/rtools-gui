"Module implementing steps for C module"
from .generic import Step, ExpansionDetection


class CExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX C"

    def run(self):
        self._boot_and_detect(r'Topaz Switch Module \(4-port\)')


class TestMII(Step):
    "Test MII"

    def run(self):
        self.set_progress(0)
        uart = self.moxtester.uart()
        uart.sendline('mii info')
        uart.expect(['PHY 0x02:'])
        uart.expect(['=>'])
        self.set_progress(1)

    @staticmethod
    def name():
        return "Test MII"

    @staticmethod
    def id():
        return "test-mii"


# All steps for MOX C in order
CSTEPS = (
    CExpansionDetection,
    TestMII,
)
