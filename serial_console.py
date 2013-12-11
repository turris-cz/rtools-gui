import serial
import time
from re import compile, search

WAITTIME = 1
WAITROUNDS = 20

class SerialConsole(object):
    def __init__(self, device, baudrate):
        super(SerialConsole, self).__init__()
        
        self.sc = serial.Serial(device, baudrate, timeout = 1)
        self.sc.write("\n")
        time.sleep(WAITTIME)
        # get the prompt, we will use it to search for
        curPrompt = self.sc.read(self.sc.inWaiting()).strip().split()[-1]
        match = search("(\w+)@(\w+):[\w/~]+#", curPrompt)
        if not match:
            self.sc.close()
            raise ValueError("Cannot find prompt on the console.")
        
        self.promptRegexp = match.group(1) + "@" + match.group(2) + ":[\w/~]+#"
    
    def close(self):
        self.sc.close()
    
    def exec_(self, cmd):
        self.sc.write(cmd.strip())
        self.sc.write("\n")
        
        consOutput = ""
        endPrompt = compile("\\n" + self.promptRegexp + "\s*$")
        
        # wait until a prompt appears
        counter = WAITROUNDS
        while True:
            time.sleep(WAITTIME)
            consOutput += self.sc.read(self.sc.inWaiting()).replace("\r", "")
            if endPrompt.search(consOutput):
                break
            elif counter == 0:
                raise IOError("I've been waiting for output too long, giving up...")
            else:
                counter -= 1
        
        # cut the command at the beginning and prompt at the end
        if consOutput.startswith(cmd):
            consOutput = consOutput[len(cmd):].strip()
        
        epMatch = endPrompt.search(consOutput)
        while epMatch:
            consOutput = consOutput[: -len(epMatch.group(0))]
            epMatch = endPrompt.search(consOutput)
        
        return consOutput.strip()
