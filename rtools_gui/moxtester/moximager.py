import os
import sys
import signal
import pexpect
import logging
import time
from .exceptions import MoxTesterImagerNoBootPrompt
from .exceptions import MoxTesterImagerFail
from .. import report


class MoxImager:
    "Moxtester mox-imager compatibility executer"
    _ERROR_REGEXP = "FAIL_"

    def __init__(self, moxtester, resources):
        self.moxtester = moxtester
        self.resources = resources

        self.pid = None
        self.pexpect = None

    def _subprocess(self, uart_sock, process_pipe, args):
        if(process_pipe[0] != 1):
            os.close(process_pipe[0])
        if(process_pipe[1] != 1):
            os.dup2(process_pipe[1], 1)
        if(process_pipe[1] != 2):
            os.dup2(process_pipe[1], 2)
        os.dup2(uart_sock, 3)
        os.close(process_pipe[1])
        logging.info("Calling {} with args '{}'".format(self.resources.mox_imager_exec, args))
        os.execl(
            self.resources.mox_imager_exec,
            self.resources.mox_imager_exec,
            '-F', '3',
            *args,
        )
        logging.error("Exec failed")

    def match(self, expected, timeout=None):
        "Wrapper around pexpect's expect that raises MoxTesterImagerFail exception"
        if self.pexpect.expect([expected, 'FAIL.*', pexpect.EOF], timeout=timeout) != 0:
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
        logging.info("Ready to start")
        # Verify bootpromt
        uart = self.moxtester.uart()
        logging.info("Got uart")
        try:
            if uart.expect(['>', 'U-Boot'], timeout=3) != 0:
                raise MoxTesterImagerNoBootPrompt()
        except pexpect.exceptions.TIMEOUT:
            raise MoxTesterImagerNoBootPrompt()
        logging.info("Got prompt")

        # Prepare and spawn mox-imager
        uart_sock = self.moxtester.uart_fileno()
        process_pipe = os.pipe2(os.O_CLOEXEC)
        logging.info("Got UART sock ({}) and PIPE ({}) to start".format(uart_sock, process_pipe))
        self.pid = None
        self.pid = os.fork()
        logging.info("Forked, PID {}".format(self.pid))
        if self.pid == 0:
            logging.info("Starting child with args {}".format(args))
            self._subprocess(uart_sock, process_pipe, args)
        os.close(process_pipe[1])
        # TODO send log to logging
        self.pexpect = pexpect.fdpexpect.fdspawn(process_pipe[0])
        return self.pexpect

    def stop(self):
        """Terminate execution"""
        exit_code = None
        if self.pid:
            os.kill(self.pid, signal.SIGKILL)
            exit_code = os.waitpid(self.pid, 0)[1]
        self.pid = None
        self.moxtester._d.default_baudrate()
        self.pexpect.close()
        self.pexpect = None
        #self.moxtester.default()
        return exit_code
