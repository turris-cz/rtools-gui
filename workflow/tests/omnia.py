import time
import re

from application import qApp, settings
from workflow.base import BaseTest, BaseWorker, spawnPexpectSerialConsole
from custom_exceptions import RunFailed


class SimpleTest(BaseTest):

    def __init__(self, name, result):
        self._name = name
        self.result = result

    def createWorker(self):
        return SimpleTestWorker(self.result)


class SimpleTestWorker(BaseWorker):
    def __init__(self, result):
        super(SimpleTestWorker, self).__init__()
        self.result = result

    def perform(self):

        for i in range(10, 101, 10):
            time.sleep(0.05)
            self.progress.emit(i)
            time.sleep(0.05)

        return self.result


class SerialNumberTest(BaseTest):
    _name = 'SERIAL NUMBER'

    def createWorker(self):
        return SerialNumberWorker(qApp.router.idHex)


class SerialNumberWorker(BaseWorker):

    def __init__(self, serial):
        super(SerialNumberWorker, self).__init__()
        self.serial = serial

    def perform(self):
        exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
        self.progress.emit(1)

        self.expectSystemConsole(exp)
        self.progress.emit(20)

        exp.sendline('atsha204cmd serial-number')
        pattern = r'[a-fA-F0-9]{16}'
        self.expect(exp, pattern)
        serial = re.search(pattern, exp.match.string).group(0)  # matches the whole string
        self.progress.emit(40)

        self.expectLastRetval(exp, 0)
        self.progress.emit(60)

        if self.serial.lower() != serial.lower():
            exp.terminate(force=True)
            raise RunFailed("Serial number doesn't match '%s' != '%s'" % (self.serial, serial))

        # try storing the firmware if the serial matches
        exp.sendline('cat /etc/git-version')
        pattern = r'[a-fA-F0-9]{40}'
        self.expect(exp, pattern)
        firmware = re.search(pattern, exp.match.string).group(0)  # matches the whole string
        self.progress.emit(80)

        self.expectLastRetval(exp, 0)
        self.progress.emit(90)

        self.firmware.emit(firmware)
        self.progress.emit(100)
        exp.terminate(force=True)
        return True


class MockTest(BaseTest):
    _name = "MOCK"

    def createWorker(self):
        return MockTestWorker()


class MockTestWorker(BaseWorker):

    def perform(self):

        exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['tester']['device'])
        self.progress.emit(1)
        exp.sendline('ls')
        self.expect(exp, '\.')
        self.progress.emit(50)
        self.expectLastRetval(exp, 0)
        self.progress.emit(100)
        exp.terminate(force=True)

        return True


TESTS = (
    SimpleTest("USB", True),
    SimpleTest("PCIA", True),
    SimpleTest("THERMOMETER", False),
    SimpleTest("GPIO", True),
    SimpleTest("CLOCK", False),
    SerialNumberTest(),
    MockTest(),
)
