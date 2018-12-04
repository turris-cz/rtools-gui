import os
import sys
import pexpect
from .exceptions import MoxTesterImagerNoBootPrompt


class MoxImager:
    "Moxtester mox-imager compatibility executer"
    _ERROR_REGEXP = "FAIL_"

    def __init__(self, moxtester, resources, serial_number, first_mac,
                 board_version):
        self.moxtester = moxtester
        self.resources = resources

        self.serial_number = serial_number
        self.first_mac = first_mac
        self.board_version = board_version

        # Variables set for caller
        self.ram = None  # Amount of ram in MiB
        self.real_serial_number = None  # Serial number as reported by mox-imager
        self.real_board_version = None  # Board version as reported by mox-imager
        self.real_fist_mac = None  # First mac address as reported by mox-imager
        self.public_key = None  # ECDSA public key
        self.exit_code = None  # Exit code of executed run
        self.all_done = False  # If everything was executed correctly

    def _subprocess(self, uart_sock, process_pipe):
        os.close(process_pipe[0])
        os.close(0)
        os.dup2(process_pipe[1], 1)
        os.dup2(process_pipe[1], 2)
        os.dup2(uart_sock, 3)
        os.execl(
            self.resources.mox_imager_exec,
            self.resources.mox_imager_exec,
            '--deploy',
            '-F', '3',
            '--serial-number', hex(self.serial_number),
            '--mac-address', self.first_mac,
            '--board-version', str(self.board_version),
            '--otp-hash', self.resources.mox_imager_secure_firmware_hash,
        )

    def run(self, callback=None):
        """Run mox-imager in OTP write mode. Returns fdexpect handle.
        callback is called to report progress. It has only one argument and
        that is floating poing between 0 and 1.
        """
        # Prepare moxtester
        self.moxtester.default()
        self.moxtester.set_boot_mode(self.moxtester.BOOT_MODE_UART)
        self.moxtester.power(True)
        self.moxtester.reset(False)
        # Verify bootpromt
        uart = self.moxtester.uart()
        try:
            if uart.expect(['>', 'U-Boot'], timeout=3) != 1:
                raise MoxTesterImagerNoBootPrompt()
        except pexpect.exceptions.TIMEOUT:
            raise MoxTesterImagerNoBootPrompt()

        # Prepare and spawn mox-imager
        uart_sock = self.moxtester.uart_fileno()
        process_pipe = os.pipe2(os.O_CLOEXEC)
        pid = os.fork()
        if not pid:
            self._subprocess(uart_sock, process_pipe)
        os.close(process_pipe[1])
        # TODO send log to logging
        fdpexp = pexpect.fdpexpect.fdspawn(process_pipe[0])

        callback(0)
        # TODO handle EOF and exceptions
        fdpexp.expect(['Sending image type TIMH'])
        callback(0.2)
        fdpexp.expect(['Sending image type WTMI'])
        callback(0.4)
        fdpexp.expect(['Found (\\d+) MiB RAM'])
        self.ram = int(fdpexp.match.group(1).decode(sys.getdefaultencoding()))
        callback(0.5)
        fdpexp.expect(['Serial Number: ([0-9A-Fa-f]+)'])
        self.real_serial_number = int(fdpexp.match.group(1).decode(sys.getdefaultencoding()), 16)
        callback(0.6)
        fdpexp.expect(['Board version: (\\d+)'])
        self.real_board_version = int(fdpexp.match.group(1).decode(sys.getdefaultencoding()))
        callback(0.7)
        fdpexp.expect(['MAC address: ([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})'])
        self.real_first_mac = ':'.join(fdpexp.match.group(i + 1).decode(sys.getdefaultencoding()) for i in range(6))
        callback(0.8)
        fdpexp.expect(['ECDSA Public Key: (0[23][0-9A-Fa-f]{132})'])
        self.public_key = fdpexp.match.group(1).decode(sys.getdefaultencoding())
        callback(0.9)
        fdpexp.expect(['All done.'])
        self.all_done = True
        callback(1)

        log.close()
        # Cleanup
        self.exit_code = os.waitpid(pid, 0)[1]
        os.close(process_pipe[0])
        os.close(uart_sock)
        self.moxtester.default()
