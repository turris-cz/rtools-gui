import threading
import os
import termios
import time
import datetime

# settings
import importlib
settings_module = os.environ.get('RTOOLS_SETTINGS', 'settings')
settings = importlib.import_module(settings_module)

PS1 = getattr(settings, 'PS1_OVERRIDE', "root@turris:/# ")
PS2 = getattr(settings, 'PS2_OVERRIDE', "> ")
UBOOT_PROMPT = getattr(settings, 'UBOOT_PROMPT_OVERRIDE', "=> ")

# following values are all in seconds
WAITTIME = 0.5
INIT_EMPTY_WAIT = 10
INIT_MAX_WAIT = 75
WRITE_TIMEOUT = 0.1


class SCError(IOError):
    # recovery types:
    IRRECOVERABLE = 0
    FACTORY_RESET = 1

    def __init__(self, msg, recovery=IRRECOVERABLE):
        super(SCError, self).__init__(msg)
        self.recovery = recovery


class SerialConsole(object):
    UNDEFINED = 0
    UBOOT = 1
    OPENWRT = 2

    FLASH_DOT_COUNT = 167
    FACTORY_RESET_NEWLINE_COUNT = 410

    def __init__(self, device, router, logdir, baudrate=termios.B115200):
        super(SerialConsole, self).__init__()

        self.state = self.UNDEFINED
        self._running = True
        self._accept_input = False
        self.inbuf = ""

        now_time = datetime.datetime.now()
        output_file_name = "sc-%s-%s.txt" % (
            router.id, now_time.strftime("%Y-%m-%d-%H-%M"))
        self._console_output_file = open(os.path.join(logdir, output_file_name), 'w', 0)

        self._sc = os.open(device, os.O_RDWR)

        try:
            # set termios flags
            newcc = termios.tcgetattr(self._sc)[6]

            # this causes read to be non-blocking (along with -ICANON)
            newcc[termios.VMIN] = 0
            newcc[termios.VTIME] = 0

            termios.tcsetattr(self._sc, termios.TCSAFLUSH, [
                termios.IGNBRK,
                0,
                termios.CS8 | termios.CREAD | termios.CLOCAL | baudrate,
                0,
                baudrate,
                baudrate,
                newcc,
            ])
            termios.tcflush(self._sc, termios.TCIOFLUSH)
        except:
            # if exception, close tty file
            try:
                os.close(self._sc)
                self._console_output_file.close()
            except:
                pass
            raise

        self._interrupt_flag = False
        self._inbuf_lock = threading.Lock()
        self._readThread = threading.Thread(target=self._readWorker)
        self._readThread.start()

    def update_progress(self, progress_bar_signal, value, max):
        if progress_bar_signal:
            percent = value * 100.0 / max
            percent = 99 if percent >= 100 else percent
            progress_bar_signal.emit(0, 100, int(percent))

    def update_time(self, time_label_signal, counter):

        if time_label_signal:
            seconds = counter * WAITTIME
            minutes = seconds / 60
            seconds %= 60
            time_label_signal.emit("%d:%02d" % (minutes, seconds))

    def to_system(self):
        """Read the output (e.g. boot messages) from
        the console and if nothing is read for INIT_EMPTY_WAIT seconds,
        it iterpretes it as 'no more boot messages'. Then it echoes \\n
        to obtain the prompt. If it fails, it retries to send \\n
        few times.

        This function either get the router to the state when it accepts
        commands or raises an SCError.
        """

        self.clear_inbuf()

        self._accept_input = True

        totalWaitCycles = int(INIT_MAX_WAIT / WAITTIME)
        noInputCycle = int(INIT_EMPTY_WAIT / WAITTIME)
        oldOutputLen = len(self.inbuf)
        while noInputCycle > 0 and totalWaitCycles > 0:
            time.sleep(WAITTIME)
            if len(self.inbuf) > oldOutputLen:
                oldOutputLen = len(self.inbuf)
                noInputCycle = int(INIT_EMPTY_WAIT / WAITTIME)
            else:
                noInputCycle -= 1
            totalWaitCycles -= 1

        if noInputCycle != 0:
            # timeouted on totalWaitCycles
            raise SCError("Too much output, as if booting was in a cycle or so...")

        # try ten times to obtain the prompt
        wCounter = 10
        read = True
        while wCounter and read:
            os.write(self._sc, "\n")
            time.sleep(WAITTIME)
            if self.inbuf.endswith("\n" + UBOOT_PROMPT):
                self.state = self.UBOOT
                raise SCError(
                    "We are in uboot, restart the router to go to the system.",
                    SCError.FACTORY_RESET)
            if self.inbuf.endswith("\n" + PS1):
                read = False
            elif self.inbuf.endswith("\n" + PS2):
                # try to reset the console
                os.write(self._sc, "\x04")
                time.sleep(WAITTIME)
                wCounter -= 1
            else:
                wCounter -= 1

        if wCounter <= 0:
            raise SCError("Could not obtain prompt.")

        self._accept_input = False
        self.state = self.OPENWRT

    def to_factory_reset(self, timeout=INIT_MAX_WAIT, worker=None):
        """this function reads output from console and when the text
        and waits for the 'procd: - init complete -' text

        This function waits at most timeout seconds, then it raises
        an exception. If timeout is -1, it waits forever.
        """
        self.clear_inbuf()

        self._interrupt_flag = False
        self._accept_input = True

        wCounter = int(timeout / WAITTIME)
        found = False
        spent_counter = 0

        while (timeout == -1 or wCounter >= 0) and not found:

            if self.inbuf.find("procd: - init complete -") > 0:
                found = True
                break

            if self._interrupt_flag:
                self._accept_input = False
                self.state = self.UNDEFINED
                raise SCError("waiting interrupted")

            time.sleep(WAITTIME)
            index = self.inbuf.rfind('Welcome in rescue mode.')
            if index > -1:
                self.update_progress(worker.updateResetProgressSig,
                                     self.inbuf[index:].count('\n'),
                                     SerialConsole.FACTORY_RESET_NEWLINE_COUNT)
            wCounter -= 1
            spent_counter += 1
            self.update_time(worker.updateResetSpentSig, spent_counter)

        if not found:
            raise SCError("Waiting for uboot messages timeouted.")

        self._accept_input = False
        self.state = self.UBOOT

    def to_flash(self, timeout=INIT_MAX_WAIT, worker=None):
        """this function reads output from console and when the text
        and waits for the 'HOTOVO' text

        This function waits at most timeout seconds, then it raises
        an exception. If timeout is -1, it waits forever.
        """

        self.clear_inbuf()

        self._interrupt_flag = False
        self._accept_input = True

        wCounter = int(timeout / WAITTIME)
        found = False
        spent_counter = 0

        while (timeout == -1 or wCounter >= 0) and not found:

            if self.inbuf.find("HOTOVO") > 0:
                found = True
                break

            if self._interrupt_flag:
                self._accept_input = False
                self.state = self.UNDEFINED
                raise SCError("waiting interrupted")

            time.sleep(WAITTIME)
            index = self.inbuf.rfind('Erase Flash Bank')
            if index > -1:
                self.update_progress(worker.updateFlashProgressSig,
                                     self.inbuf[index:].count('.'),
                                     SerialConsole.FLASH_DOT_COUNT)
            wCounter -= 1
            spent_counter += 1
            self.update_time(worker.updateFlashSpentSig, spent_counter)

        if not found:
            raise SCError("Waiting for uboot messages timeouted.")

        self._accept_input = False
        self.state = self.UBOOT

    def interrupt_wait(self):
        self._interrupt_flag = True

    def _readWorker(self):
        while self._running:
            tmps = os.read(self._sc, 16).replace("\r", "")
            if self._accept_input and tmps:
                with self._inbuf_lock:
                    self.inbuf += tmps
                    self._console_output_file.write(tmps)
            time.sleep(0.0003)

    def allow_input(self):
        self._accept_input = True

    def disable_input(self):
        self._accept_input = False

    def close(self):
        self._running = False
        self._readThread.join()
        os.close(self._sc)
        self._console_output_file.close()

    def clear_inbuf(self):
        with self._inbuf_lock:
            self.inbuf = ""

    def writeLine(self, text):
        if not self._accept_input:
            raise ValueError("Allow accepting of input before running writeLine")

        for c in text[:-1]:
            if c == "\n":
                raise ValueError("SerialConsole.writeLine(text) accepts only one line of a text")

        # write characters
        inLength = len(self.inbuf)
        for c in text:
            os.write(self._sc, c)
            blocked = True
            wCounter = int(WRITE_TIMEOUT / 0.001)
            while blocked:
                time.sleep(0.001)
                newPart = self.inbuf[inLength:]
                wCounter -= 1
                if not newPart:
                    if wCounter > 0:
                        continue
                    else:
                        raise SCError("Written character not echoed back.")
                elif newPart == c or c == "\n" and newPart[0] == "\n":
                    # written character has been read
                    blocked = False
                    inLength += 1
                elif newPart == c + "\n" or newPart == "\n" + c:
                    blocked = False
                    inLength += 2
                elif newPart == "\n":
                    inLength += 1
                    # stay blocked
                else:
                    raise SCError("unexpected characters in inbuf")

        return inLength

    def exec_(self, cmd, timeout=10, wait_interval=WAITTIME):
        """exec_(cmd, timeout=10)
        Execute given command or script. It must be a
        single command (output expected only after the whole command written),
        but can span multiple lines.

        Timeout denotes how much time it waits for the command to finish (and the prompt
        to be displayed at the end. It is in seconds.
        """
        if self.state == self.OPENWRT:
            prompt = PS1
        elif self.state == self.UBOOT:
            prompt = UBOOT_PROMPT
        else:
            raise ValueError("Connection in undefined state, call to_system or to_uboot before.")

        self.clear_inbuf()

        self._accept_input = True

        lines = cmd.strip().replace("\r", "").split("\n")
        cmdLen = 0
        for l in lines[:-1]:
            # write the line
            cmdLen += self.writeLine(l + "\n")

            # wait for prompt PS2
            wCounter = 50
            while wCounter and not self.inbuf.endswith(PS2):
                time.sleep(0.001)
                wCounter -= 1

            if wCounter <= 0:
                raise SCError("Expected prompt not found")

            cmdLen += len(PS2)

        cmdLen += self.writeLine(lines[-1] + "\n")

        wCounter = int(timeout / wait_interval)
        while wCounter >= 0 and not self.inbuf.endswith(prompt):
            time.sleep(wait_interval)
            wCounter -= 1

        if wCounter < 0:
            raise SCError("Expected prompt not found")

        self._accept_input = False

        return self.inbuf[cmdLen: -len(prompt)]

    def read_firmware_version(self):
        stdOut = self.exec_('cat /etc/git-version')
        cmdStatus = self.lastStatus()
        return cmdStatus == "0", stdOut

    def lastStatus(self):
        """Return status of the last command run with SerialConsole.exec_().
        It returns string as obtained from running "echo $?" with whitespaces
        removed from the end.
        """
        return self.exec_("echo $?").rstrip()
