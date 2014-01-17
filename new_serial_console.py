import termios
import time


PROMPT = "@@turris@@"

# following values are all in seconds
WAITTIME = 0.5
INIT_EMPTY_WAIT = 5
INIT_MAX_WAIT = 80


class SerialConsole(object):
    """SerialConsole(device, baudrate) -> serial console object
    device - tty device (/dev/tty*)
    baudrate - must be one of 
"""
    def __init__(self, device, baudrate=termios.B115200):
        super(SerialConsole, self).__init__()
        print "      init started"
        print "~~~~~~~~~~~~~~~~~~~~~~~"
        # check if baudrate supported
        if baudrate not in [getattr(termios, x)
                            for x in dir(termios)
                            if x.startswith("B") and x[1:].isdigit()]:
            raise ValueError("Unsupported baudrate")
        
        self._device = device
        self._sc = open(self._device, 'r+')
        
        try:
            # set termios flags
            newcc = termios.tcgetattr(self._sc.fileno())[6]
            
            # this causes read to be non-blocking (along with -ICANON)
            newcc[termios.VMIN] = 0
            newcc[termios.VTIME] = 0
            
            termios.tcsetattr(self._sc.fileno(), termios.TCSAFLUSH, [
                    termios.IGNBRK,
                    0,
                    termios.CS8 | termios.CREAD | termios.CLOCAL | baudrate,
                    0,
                    baudrate,
                    baudrate,
                    newcc,
                    ])
            
            
            # try to find a prompt
            # 1. wait for no more input here
            # 2. echo \n and you should get a prompt
            
            # tcflush(sc.fileno(), TCIOFLUSH)
            
            totalWaitCycles = int(INIT_MAX_WAIT / WAITTIME)
            noInputCycle = int(INIT_EMPTY_WAIT / WAITTIME)
            while noInputCycle > 0 and totalWaitCycles > 0:
                time.sleep(WAITTIME)
                outData = self._sc.read() # this read is non-blocking
                print ">~>", repr(outData)
                if outData:
                    noInputCycle = 10
                else:
                    noInputCycle -= 1
                
                totalWaitCycles -= 1
            
            if noInputCycle != 0:
                # timeouted on totalWaitCycles
                raise IOError("Too much output, as if booting was in a cycle or so...")
            
            self._sc.write("\n")
            time.sleep(WAITTIME)
            print self._sc.read()
        except:
            # if exception, close tty file
            try:
                self._sc.close()
            except:
                pass
            raise
        print "~~~~~~~~~~~~~~~~~~~~~~~"
        print "     init finished"

sc = SerialConsole("/dev/ttyUSB0")

# set rtscts on router side
sc._sc.write("stty -F /dev/ttyS0 crtscts\n")
time.sleep(0.5)
print sc._sc.read()
time.sleep(0.5)
print "if 0, rtscts has been set correctly"
sc._sc.write("echo $?\n")
time.sleep(0.5)
print sc._sc.read()

# here we get input overruns once in a while
for x in xrange(1000):
    sc._sc.write("echo 'nejaky text nejaky text'\n")
    time.sleep(0.1)
    print sc._sc.read()
    time.sleep(0.1)




# sc.write("stty -F /dev/ttyS0 -echo\n")
# sc.write("PS1=\n")
# sc.write("PS2=''\n")

# try echo nieco if we get 'nieco+prompt'

# init finished

# exec_ now consist only of write followed by read        



import threading
import os
import time


PS1 = "root@turris:/# "
PS2 = "> "

class SerialConsole(object):
    def __init__(self):
        super(SerialConsole, self).__init__()
        self.dbg_list = []
        self._running = True
        self._acceptInput = False
        self.inbuf = ""
        
        self._sc = os.open("/dev/ttyUSB0", os.O_RDWR)
        
        self._readThread = threading.Thread(target=self._readWorker)
        self._readThread.start()
    
    def _readWorker(self):
        dbg_waitcycle = 0
        while self._running:
            tmps = os.read(self._sc, 16).replace("\r", "")
            if self._acceptInput and tmps:
                self.dbg_list.append(dbg_waitcycle)
                dbg_waitcycle = 0
                self.inbuf += tmps
            else:
                dbg_waitcycle += 1
            time.sleep(0.0003)
    
    def close(self):
        self._running = False
        self._readThread.join()
        os.close(self._sc)
    
    def writeLine(self, text):
        if not self._acceptInput:
            raise IOError("Allow accepting of input before running writeLine")
        
        for c in text[:-1]:
            if c == "\n":
                raise ValueError("SerialConsole.writeLine(text) accepts only one line of a text")
        
        # write characters
        for c in text:
            inLength = len(self.inbuf)
            os.write(self._sc, c)
            blocked = True
            while blocked:
                time.sleep(0.001)
                newPart = self.inbuf[inLength:]
                if not newPart or newPart == "\n":
                    continue
                elif newPart == c or newPart == c + "\n" or newPart == "\n" + c:
                    blocked = False
                elif c == "\n" and newPart.startswith("\n"):
                    blocked = False
                else:
                    print "ojojoj >" + repr(newPart) + "<"
                    raise IOError("unexpected characters in inbuf")
    
    def exec_(self, text):
        """Execute remotely given command or script. It must be a
        single command, but can span multiple lines.
        """
        
        self.inbuf = ""
        self._acceptInput = True
        
        lines = text.strip().replace("\r", "").split("\n")
        for l in lines[:-1]:
            # write the line
            self.writeLine(l + "\n")
            
            # wait for prompt PS2
            wCounter = 50
            while wCounter and not self.inbuf.endswith(PS2):
                time.sleep(0.001)
                wCounter -= 1
                
            if wCounter <= 0:
                raise IOError("Expected prompt not found")
            
        self.writeLine(lines[-1] + "\n")
        
        wCounter = 20
        while wCounter and not self.inbuf.endswith(PS1):
            time.sleep(0.5)
            wCounter -= 1
        
        if wCounter <= 0:
            raise IOError("Expected prompt not found")


sc = SerialConsole()

            # DEBUG
            #if c!= "\n" and self.inbuf[-1] != c:
            #    print "===========\ndebug START\n===========\nnew character, but not same as written\ntext:"
            #    print text
            #    print "output from router"
            #    print self.inbuf
            #    print "=========\ndebug END\n========="
            
       
