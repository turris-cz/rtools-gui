import threading
import os
import termios
import time


PS1 = "root@turris:/# "
PS2 = "> "
UBOOT_PROMPT = "=> "

# following values are all in seconds
WAITTIME = 0.5
INIT_EMPTY_WAIT = 5
INIT_MAX_WAIT = 75
WRITE_TIMEOUT = 0.1


class SCError(IOError):
    pass


class SerialConsole(object):
    UNDEFINED = 0
    UBOOT = 1
    OPENWRT = 2
    
    def __init__(self, device, baudrate=termios.B115200):
        super(SerialConsole, self).__init__()
        
        self.state = self.UNDEFINED
        self._running = True
        self._accept_input = False
        self.inbuf = ""
        
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
        except:
            # if exception, close tty file
            try:
                os.close(self._sc)
            except:
                pass
            raise
        
        self._inbuf_lock = threading.Lock()
        self._readThread = threading.Thread(target=self._readWorker)
        self._readThread.start()
    
    def to_system(self):
        """Read the output (e.g. boot messages) from
        the console and if nothing is read for INIT_EMPTY_WAIT seconds,
        it iterpretes it as 'no more boot messages'. Then it echoes \\n
        to obtain the prompt. If it fails, it retries to send \\n
        few times.
        
        This function either get the router to the state when it accepts
        commands or raises an SCError.
        """
        
        with self._inbuf_lock:
            self.inbuf = ""
        self._accept_input = True
        
        totalWaitCycles = int(INIT_MAX_WAIT / WAITTIME)
        noInputCycle = int(INIT_EMPTY_WAIT / WAITTIME)
        while noInputCycle > 0 and totalWaitCycles > 0:
            time.sleep(WAITTIME)
            if self.inbuf:
                noInputCycle = int(INIT_EMPTY_WAIT / WAITTIME)
                with self._inbuf_lock:
                    self.inbuf = ""
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
                raise SCError("We are in uboot, restart the router to go to the system.")
            if self.inbuf.endswith("\n" + PS1):
                read = False
            else:
                wCounter -= 1
        
        if wCounter <= 0:
            raise SCError("Could not obtain prompt.")
        
        self._accept_input = False
        self.state = self.OPENWRT
    
    def to_uboot(self):
        """this function reads output from console and when the text
        "Hit any key to stop autoboot" is read, it sends ' ' (space) to
        interrupt the autoboot. Then it waits for $UBOOT_PROMPT.
        
        If operating system prompt is found (denoting that os is running)
        it raises an exception.
        """
        
        with self._inbuf_lock:
            self.inbuf = ""
        
        self._accept_input = True
        
        waitCycles = int(INIT_MAX_WAIT / 0.001)
        waiting = True
        while waitCycles > 0 and waiting:
            if self.inbuf.find("Hit any key to stop autoboot") != -1:
                # send ' ' to interrupt autoboot
                os.write(self._sc, ' ')
                waiting = False
            time.sleep(0.001)
            waitCycles -= 1
        
        wCounter = int(INIT_MAX_WAIT / WAITTIME)
        while wCounter and not self.inbuf.endswith(UBOOT_PROMPT):
            os.write(self._sc, "\n")
            if self.inbuf.find("\n" + PS1) != -1 or self.inbuf.find("\n" + PS2) != -1:
                self._accept_input = False
                self.state = self.OPENWRT
                raise SCError("OS prompt found, restart the device")
            time.sleep(WAITTIME)
            wCounter -= 1
        
        if waiting:
            raise SCError("Waiting for uboot messages timeouted.")
        
        if wCounter <= 0:
            raise SCError("Could not get uboot prompt after interrupting autoboot")
        
        self._accept_input = False
        self.state = self.UBOOT
    
    def _readWorker(self):
        while self._running:
            tmps = os.read(self._sc, 16).replace("\r", "")
            if self._accept_input and tmps:
                with self._inbuf_lock:
                    self.inbuf += tmps
            time.sleep(0.0003)
    
    def allow_input(self):
        self._accept_input = True
    
    def disable_input(self):
        self._accept_input = False
    
    def close(self):
        self._running = False
        self._readThread.join()
        os.close(self._sc)
    
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
                if not newPart:
                    if wCounter > 0:
                        continue
                    else:
                        IOError("Written character not echoed back.")
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
    
    def exec_(self, cmd, timeout=10):
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
        
        with self._inbuf_lock:
            self.inbuf = ""
        
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
        
        wCounter = int(timeout / WAITTIME)
        while wCounter and not self.inbuf.endswith(prompt):
            time.sleep(WAITTIME)
            wCounter -= 1
        
        if wCounter <= 0:
            raise SCError("Expected prompt not found")
        
        self._accept_input = False
        
        return self.inbuf[cmdLen: -len(prompt)]
    
    def lastStatus(self):
        """Return status of the last command run with SerialConsole.exec_().
        It returns string as obtained from running "echo $?" with whitespaces
        removed from the end.
        """
        return self.exec_("echo $?").rstrip()
