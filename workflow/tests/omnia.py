import time
import re

from application import qApp
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

        for i in range(0, 100, 10):
            time.sleep(0.05)
            self.progress.emit(10)
            time.sleep(0.05)

        return self.result


class FirmwareTest(BaseTest):
    _name = 'FIRMWARE'

    def createWorker(self):
        return FirmwareTestWorker()

class FirmwareTestWorker(BaseWorker):
    def perform(self):
        exp = spawnPexpectSerialConsole()
        self.progress.emit(1)

        self.expectSystemConsole(exp)
        self.progress.emit(29)

        exp.sendline('cat /etc/git-version')
        pattern = r'[a-fA-F0-9]{40}'
        exp.expect(pattern)
        firmware = re.search(pattern, exp.match.string).group(0)  # matches the whole string
        self.progress.emit(30)

        self.expectLastRetval(exp, 0)
        self.progress.emit(30)

        self.firmware.emit(firmware)
        self.progress.emit(10)

        exp.terminate(force=True)
        return True


class SerialNumberTest(BaseTest):
    _name = 'SERIAL NUMBER'

    def createWorker(self):
        return SerialNumberWorker(qApp.router.idHex)

class SerialNumberWorker(BaseWorker):

    def __init__(self, serial):
        super(SerialNumberWorker, self).__init__()
        self.serial = serial

    def perform(self):
        exp = spawnPexpectSerialConsole()
        self.progress.emit(1)

        self.expectSystemConsole(exp)
        self.progress.emit(29)

        exp.sendline('atsha204cmd serial-number')
        pattern = r'[a-fA-F0-9]{16}'
        exp.expect(pattern)
        serial = re.search(pattern, exp.match.string).group(0)  # matches the whole string
        self.progress.emit(30)

        self.expectLastRetval(exp, 0)
        self.progress.emit(30)

        if self.serial.lower() != serial.lower():
            raise RunFailed("Serial number doesn't match '%s' != '%s'" % (self.serial, serial))
        self.progress.emit(10)

        exp.terminate(force=True)
        return True


TESTS = (
    SimpleTest("USB", True),
    SimpleTest("PCIA", True),
    SimpleTest("THERMOMETER", False),
    SimpleTest("GPIO", True),
    SimpleTest("CLOCK", False),
    FirmwareTest(),
    SerialNumberTest(),
)
