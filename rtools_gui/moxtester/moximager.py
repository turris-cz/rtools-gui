import os
import sys
import fcntl
import pexpect
from pexpect import fdpexpect


class MoxImager:
    "Moxtester mox-imager compatibility executer"
    _ERROR_REGEXP = "FAIL_"

    def __init__(self, moxtester, resources, serial_number, first_mac,
                 board_version=22):
        self.moxtester = moxtester
        self.resources = resources

        self.serial_number = serial_number
        self.first_mac = first_mac
        self.board_version = board_version

        # TODO verify executable and so on

        # Variables set for caller
        self.exit_code = None  # Exit code of executed run
        self.all_done = False  # If everything was executed correctly
        # TODO

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
        "Run mox-imager in OTP write mode. Returns fdexpect handle."
        # Prepare moxtester
        self.moxtester.default()
        self.moxtester.set_boot_mode(self.moxtester.BOOT_MODE_UART)
        self.moxtester.power(True)
        self.moxtester.reset(False)
        # Verify bootpromt
        with self.moxtester.uart() as uart:
            uart.expect(['>'], timeout=3)
            # TODO catch timeout and raise different exception

        # Prepare and spawn mox-imager
        uart_sock = self.moxtester.uart_fileno()
        process_pipe = os.pipe2(os.O_CLOEXEC)
        pid = os.fork()
        if not pid:
            self._subprocess(uart_sock, process_pipe)
        os.close(process_pipe[1])
        # TODO send log to logging
        log = open('mox-imager.log', 'wb')
        fdpexp = fdpexpect.fdspawn(process_pipe[0], logfile=log)

        # Go trough mox-imager output
        # TODO
        fdpexp.expect(['All done.', pexpect.EOF])
        self.all_done = True

        log.close()
        # Cleanup
        self.exit_code = os.waitpid(pid, 0)[1]
        os.close(process_pipe[0])
        os.close(uart_sock)
        self.moxtester.default()
