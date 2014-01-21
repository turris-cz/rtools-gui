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


class SCError(IOError):
    pass


class SerialConsole(object):
    def __init__(self, device, baudrate=termios.B115200):
        super(SerialConsole, self).__init__()
        
        # self.state = self.UNDEFINED # TODO add states - UNDEFINED, UBOOT, SYSTEM
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
            else:
                noInputCycle -= 1
                totalWaitCycles -= 1
                
            with self._inbuf_lock:
                self.inbuf = ""
        
        if noInputCycle != 0:
            # timeouted on totalWaitCycles
            raise SCError("Too much output, as if booting was in a cycle or so...")
            
        # try ten times to obtain the prompt
        wCounter = 10
        read = True
        while wCounter and read:
            os.write(self._sc, "\n")
            time.sleep(WAITTIME)
            if self.inbuf.endswith(PS1):
                read = False
            else:
                wCounter -= 1
        
        if wCounter <= 0:
            raise SCError("Could not obtain prompt.")
        
        with self._inbuf_lock:
            self.inbuf = ""
    
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
                raise SCError("OS prompt found, restart the device")
            time.sleep(WAITTIME)
            wCounter -= 1
        
        if waiting:
            raise SCError("Waiting for uboot messages timeouted.")
        
        if wCounter <= 0:
            raise SCError("Could not get uboot prompt after interrupting autoboot")
        
        self._accept_input = False
    
    def _readWorker(self):
        while self._running:
            tmps = os.read(self._sc, 16).replace("\r", "")
            if self._accept_input and tmps:
                with self._inbuf_lock:
                    self.inbuf += tmps
            time.sleep(0.0003)
    
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
            while blocked:
                time.sleep(0.001)
                newPart = self.inbuf[inLength:]
                if not newPart:
                    continue            # TODO add timeout because now it can cause an infinite loop
                elif newPart == c or c == "\n" and newPart[0] == "\n":
                    # written character has been read
                    blocked = False
                    inLength += 1
                elif newPart == c + "\n" or newPart == "\n" + c:
                    blocked = False
                    inLength += 2
                else:
                    raise SCError("unexpected characters in inbuf")
        
        return inLength
    
    def exec_(self, text):
        """Execute given command or script. It must be a
        single command (output expected only after whole text written),
        but can span multiple lines.
        """
        
        with self._inbuf_lock:
            self.inbuf = ""
        
        self._accept_input = True
        
        lines = text.strip().replace("\r", "").split("\n")
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
        
        wCounter = 20
        while wCounter and not self.inbuf.endswith(PS1):
            time.sleep(0.5)
            wCounter -= 1
        
        if wCounter <= 0:
            raise SCError("Expected prompt not found")
        
        self._accept_input = False
        
        return self.inbuf[cmdLen: -len(PS1)]


# sc = SerialConsole("/dev/ttyUSB0")
       
# sc.exec_("reboot\n")
# sc.to_uboot()
