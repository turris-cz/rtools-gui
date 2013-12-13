import serial
import time
from re import compile, search

WAITTIME = 1
WAITROUNDS = 20

class SerialConsole(object):
    def __init__(self, device, baudrate):
        super(SerialConsole, self).__init__()
        
        self._device = device
        self._baudrate = baudrate
        self._sc = serial.Serial(self._device, self._baudrate, timeout = 1)
        
        # if booting up, read the log until no output in WAITTIME seconds
        # try it 5 times
        bootLog = "1"
        #attempt = 4
        #while
        while bootLog:
            time.sleep(WAITTIME)
            bootLog = self._sc.read(self._sc.inWaiting())
            print ">" + bootLog + "<"
        print "i think that there's no more bootLog"
        
        self._sc.write("\r\n")
        time.sleep(WAITTIME)
        # get the prompt, we will use it to search for
        curPrompt = self._sc.read(self._sc.inWaiting()).strip()
        if not curPrompt:
            raise ValueError("Cannot find prompt on the console.")
        curPrompt = curPrompt.split()[-1]
        match = search("(\w+)@(\w+):[\w/~]+#", curPrompt)
        if not match:
            self._sc.close()
            raise ValueError("Cannot find prompt on the console.")
        
        self.promptRegexp = match.group(1) + "@" + match.group(2) + ":[\w/~]+#"
    
    def close(self):
        self._sc.close()
        self._sc = None
    
    def reopen(self):
        if self._sc:
            self._sc.close()
        self._sc = serial.Serial(self._device, self._baudrate, timeout = 1)
    
    def exec_(self, cmd):
        self._sc.write(cmd.strip())
        self._sc.write("\r\n")
        
        consOutput = ""
        endPromptRegexp = compile("\n" + self.promptRegexp + "\s*$")
        
        # wait until a prompt appears
        counter = WAITROUNDS
        while True:
            time.sleep(WAITTIME)
            consOutput += self._sc.read(self._sc.inWaiting()).replace("\r", "")
            match = endPromptRegexp.search(consOutput)
            if match:
                strEndPrompt = match.group(0).strip()
                break
            elif counter == 0:
                raise IOError("I've been waiting for output too long, giving up...")
            else:
                counter -= 1
        
        # cut the command at the beginning and prompt at the end
        if consOutput.startswith(cmd):
            consOutput = consOutput[len(cmd):].strip()
        
        while consOutput.endswith(strEndPrompt):
            consOutput = consOutput[: -len(strEndPrompt)].rstrip()
        
        return consOutput.strip()
