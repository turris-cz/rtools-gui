from .exceptions import FatalWorkflowException
from ..moxtester.exceptions import MoxTesterImagerNoBootPrompt


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
    def id():
        "Identifier used to identify this step in database and other places."
        raise NotImplementedError()

    @staticmethod
    def name():
        "Returns name of this test. In Czech of course."
        raise NotImplementedError()


class ExpansionDetection(Step):
    "Generic expansion board detection step durring u-boot boot"

    def _boot_and_detect(self, board_str):
        "Boot board and detect given string as board"
        self.set_progress(0)
        self.moxtester.power(True)
        uart = self.moxtester.uart()
        self.moxtester.reset(False)
        self.set_progress(.1)
        uart.expect(['U-Boot'])
        self.set_progress(.2)
        res = uart.expect(['Module Topology:', 'Hit any key to stop autoboot'])
        if res != 0:
            raise FatalWorkflowException(
                """Rozšiřující deska nebyla pravděpodobně vložena nebo ji
                nebylo možné detekovat!""")
        self.set_progress(.4)
        res = uart.expect(['1: ' + board_str, 'Hit any key to stop autoboot'])
        if res != 0:
            raise FatalWorkflowException(
                "Rozšiřující deska byla detekována jako špatný typ!")
        self.set_progress(.8)
        uart.expect(['Hit any key to stop autoboot'])
        self.set_progress(.9)
        uart.sendline('')
        self.set_progress(.95)
        uart.expect(['=>'])
        self.set_progress(1)

    @staticmethod
    def name():
        return "Detekce rozpoznání a přítomnosti"

    @staticmethod
    def id():
        return "expansion-detect"

class OTPProgramming(Step):
    "Program OTP memory"

    def run(self):
        if self.conf.no_otp:
            return  # Do nothing for untrusted run
        imager = self.moxtester.mox_imager(self.resources)
        failed = False
        ram = None  # Amount of ram in MiB
        real_serial_number = None  # Serial number as reported by mox-imager
        real_board_version = None  # Board version as reported by mox-imager
        real_fist_mac = None  # First mac address as reported by mox-imager
        public_key = None  # ECDSA public key
        exit_code = None  # Exit code of executed run
        all_done = False  # If everything was executed correctly

        try:
            imager.run(
                '--deploy',
                '--serial-number', hex(self.serial_number),
                '--mac-address', self.db_board.mac_wan(),
                '--board-version', str(self.db_board.revision()),
                '--otp-hash', self.otp_hash()
            )
            try:
                self.set_progress(0)
                imager.match('Sending image type TIMH')
                self.set_progress(0.2)
                imager.match('Sending image type WTMI')
                self.set_progress(0.4)
                ram = int(imager.match('Found (\\d+) MiB RAM')[1].decode())
                self.set_progress(0.5)
                real_serial_number = int(imager.match('Serial Number: ([0-9A-Fa-f]+)')[1].decode(), 16)
                self.set_progress(0.6)
                real_board_version = int(imager.match('Board version: (\\d+)')[1].decode())
                self.set_progress(0.7)
                real_first_mac = ':'.join(imager.match('MAC address: ([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})')[1:])
                self.set_progress(0.8)
                public_key = imager.match('ECDSA Public Key: (0[23][0-9A-Fa-f]{132})')[1].decode()
                self.set_progress(0.9)
                imager.match('All done.')
                all_done = True
                self.set_progress(1)
            finally:
                exit_code = imager.stop()
        except MoxTesterImagerNoBootPrompt:
            failed = True
        recorded = self.db_board.core_info()
        # TODO we can verify here if this is mox with correct sticker
        if recorded is not None:
            if not failed and (recorded['mem'] != ram or recorded['key'] != public_key):
                return "DB value does not match:\nRam: {} : {}\nKey: {} : {}".format(
                    recorded['mem'], ram, recorded['key'], public_key)
            return None
        if failed:
            raise FatalWorkflowException("OTP programming failed")
        self.db_board.set_core_info(ram, public_key)
        return None

    @staticmethod
    def name():
        return "Programování OTP"

    @staticmethod
    def id():
        return "otp-program"
