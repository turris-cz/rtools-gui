import os
import sys
import signal
import pexpect
from .exceptions import MoxTesterImagerNoBootPrompt
from .exceptions import MoxTesterImagerFail


class MoxImager:
    "Moxtester mox-imager compatibility executer"
    _ERROR_REGEXP = "FAIL_"

    def __init__(self, moxtester, resources):
        self.moxtester = moxtester
        self.resources = resources

        self.pid = None
        self.pexpect = None

    def _subprocess(self, uart_sock, process_pipe, args):
        os.close(process_pipe[0])
        os.close(0)
        os.dup2(process_pipe[1], 1)
        os.dup2(process_pipe[1], 2)
        os.dup2(uart_sock, 3)
        os.execl(
            self.resources.mox_imager_exec,
            self.resources.mox_imager_exec,
            '-F', '3',
            *args
        )

    def match(self, expected):
        "Wrapper around pexpect's expect that raises MoxTesterImagerFail exception"
        if self.pexpect.expect([expected, 'FAIL.*', pexpect.EOF], timeout=None) != 0:
            raise MoxTesterImagerFail("EOF" if self.pexpect.match == pexpect.EOF else self.pexpect.match.string)
        return self.pexpect.match.groups()

    def run(self, *args):
        """Run mox-imager in OTP write mode. Returns fdexpect handle.
        callback is called to report progress. It has only one argument and
        that is floating poing between 0 and 1.
        """
        assert(self.pid is None)
        # Prepare moxtester
        self.moxtester.default()
        self.moxtester.set_boot_mode(self.moxtester.BOOT_MODE_UART)
        self.moxtester.power(True)
        self.moxtester.reset(False)
        # Verify bootpromt
        uart = self.moxtester.uart()
        try:
            if uart.expect(['>', 'U-Boot'], timeout=3) != 0:
                raise MoxTesterImagerNoBootPrompt()
        except pexpect.exceptions.TIMEOUT:
            raise MoxTesterImagerNoBootPrompt()

        # Prepare and spawn mox-imager
        uart_sock = self.moxtester.uart_fileno()
        process_pipe = os.pipe2(os.O_CLOEXEC)
        self.pid = os.fork()
        if not self.pid:
            self._subprocess(uart_sock, process_pipe, args)
        os.close(process_pipe[1])
        # TODO send log to logging
        self.pexpect = pexpect.fdpexpect.fdspawn(process_pipe[0])
        self.pexpect.logfile = os.fdopen(sys.stdout.fileno(), 'wb')
        return self.pexpect

    def stop(self):
        """Terminate execution"""
        os.kill(self.pid, signal.SIGKILL)
        exit_code = os.waitpid(self.pid, 0)[1]
        self.pexpect.close()
        #self.moxtester.default()
        return exit_code
