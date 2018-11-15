from .exceptions import FatalWorkflowException


class Step:
    "Abstract class for signle step"

    def __init__(self, serial_number, moxtester, conf, resources, db_board, set_progress):
        self.serial_number = serial_number
        self.moxtester = moxtester
        self.conf = conf
        self.resources = resources
        self.db_board = db_board
        self.set_progress = set_progress

    def run(self):
        "Run this step"
        raise NotImplementedError()

    @staticmethod
    def name():
        "Returns name of this test. In Czech of course."
        raise NotImplementedError()

    @staticmethod
    def dbid():
        "Identifier used in database for this step."
        raise NotImplementedError()


class ExpansionDetection(Step):
    "Generic expansion board detection step durring u-boot boot"

    def _boot_and_detect(self, board_str):
        "Boot board and detect given string as board"
        self.set_progress(0)
        self.moxtester.power(True)
        with self.moxtester.uart() as uart:
            self.moxtester.reset(False)
            self.set_progress(10)
            uart.expect(['U-Boot'])
            self.set_progress(20)
            res = uart.expect(['Module Topology:', 'Hit any key to stop autoboot'])
            if res != 0:
                raise FatalWorkflowException(
                    """Rozšiřující deska nebyla pravděpodobně vložena nebo ji
                    nebylo možné detekovat!""")
            self.set_progress(40)
            res = uart.expect(['1: ' + board_str, 'Hit any key to stop autoboot'])
            if res != 0:
                raise FatalWorkflowException(
                    "Rozšiřující deska byla detekována jako špatný typ!")
            self.set_progress(80)
            uart.expect(['Hit any key to stop autoboot'])
            self.set_progress(90)
            uart.sendline('')
            self.set_progress(95)
            uart.expect(['=>'])
            self.set_progress(100)

    @staticmethod
    def name():
        return "Detekce rozpoznání a přítomnosti"

    @staticmethod
    def dbid():
        return "expansion-detect"
