import serial
import time
from re import compile, search

WAITTIME = 1 # waittime should not be too short to be able to detect end of boot messages
WAITROUNDS = 10
BOOTWAITROUNDS = 6 * WAITROUNDS
WRITESLEEP = 0.001

class SerialConsole(object):
    def __init__(self, device, baudrate):
        super(SerialConsole, self).__init__()
        
        self._device = device
        self._baudrate = baudrate
        self._sc = serial.Serial(self._device, self._baudrate, timeout = 1)
        
        try:
            # if booting up, read the log until prompt found
            counter = BOOTWAITROUNDS
            lastOutput = "1"
            consOutput = ""
            
            while True:
                if not lastOutput:
                    self._sc.write("\r\n")
                time.sleep(WAITTIME)
                lastOutput = self._sc.read(self._sc.inWaiting()).replace("\r", "")
                consOutput += lastOutput
                match = search(r"(\w+)@(\w+):[\w/~]+#\s*$", consOutput)
                if match:
                    self.promptRegexp = match.group(1) + "@" + match.group(2) + r":[\w/~]+#"
                    break
                elif counter <= 0:
                    raise IOError("I've been waiting for prompt too long, giving up...")
                else:
                    counter -= 1
        except Exception:
            self._sc.close()
            self._sc = None
            raise
        
        # we should get no more output here
        time.sleep(WAITTIME)
        oBufChars = self._sc.inWaiting()
        while oBufChars:
            self._sc.read(oBufChars)
            time.sleep(WAITTIME)
            oBufChars = self._sc.inWaiting()
    
    def close(self):
        self._sc.close()
        self._sc = None
    
    def reopen(self):
        if self._sc:
            self._sc.close()
        self._sc = serial.Serial(self._device, self._baudrate, timeout = 1)
    
    def exec_(self, cmd):
        # cmd should use unix newline (\n)
        cmd = cmd.replace("\r\n","\n").replace("\r","\n").strip()
        
        # clear if there is something in the buffer
        # self._sc.read(self._sc.inWaiting())
        self._sc.flushInput()
        self._sc.flushOutput()
        for x in cmd:
            time.sleep(WRITESLEEP)
            self._sc.write(x)
        time.sleep(WRITESLEEP)
        self._sc.write("\n")
        
        consOutput = ""
        endPromptRegexp = compile(self.promptRegexp + r"\s*$")
        
        # wait until a prompt appears
        counter = WAITROUNDS
        while True:
            time.sleep(WAITTIME)
            consOutput += self._sc.read(self._sc.inWaiting()).replace("\r", "")
            match = endPromptRegexp.search(consOutput)
            if match:
                break
            elif counter == 0:
                raise IOError("I've been waiting for output too long, giving up...")
            else:
                counter -= 1
        
        # cut the command at the beginning and prompt at the end
        consOutput = consOutput.split("\n")
        cmdLines = len(cmd.split("\n"))
        
        if cmd.startswith(consOutput[0]):
            consOutput = "\n".join(consOutput[cmdLines:])
        
        match = endPromptRegexp.search(consOutput)
        while match:
            consOutput = consOutput[: -len(match.group(0))].rstrip()
            match = endPromptRegexp.search(consOutput)
        
        return consOutput.strip()
    
    def lastStatus(self):
        return self.exec_("echo $?")
