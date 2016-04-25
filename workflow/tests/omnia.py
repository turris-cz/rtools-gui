import locale
import math
import time

from application import qApp, settings
from datetime import datetime
from workflow.base import BaseTest, BaseWorker, spawnPexpectSerialConsole
from custom_exceptions import RunFailed


class SimpleTest(BaseTest):

    def __init__(self, name, result):
        self._name = name
        self.result = result

    def createWorker(self):
        return self.Worker(self.result)

    class Worker(BaseWorker):
        def __init__(self, result):
            super(SimpleTest.Worker, self).__init__()
            self.result = result

        def perform(self):

            for i in range(10, 101, 10):
                time.sleep(0.05)
                self.progress.emit(i)
                time.sleep(0.05)

            return self.result


class UsbTest(BaseTest):
    _name = 'USB'

    def __init__(self, usb_count):
        self.usb_count = usb_count

    def createWorker(self):
        return self.Worker(self.usb_count)

    class Worker(BaseWorker):

        def __init__(self, usb_count):
            super(UsbTest.Worker, self).__init__()
            self.usb_count = usb_count

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(20)

            exp.sendline('echo "###$(ls /dev/sd? 2> /dev/null | wc -l)###"')

            pattern = r'###[0-9]+###'
            self.expect(exp, pattern)
            usb_count = exp.match.group()
            self.progress.emit(50)

            try:
                usb_count = int(usb_count.strip().strip("#"))
            except ValueError:
                raise RunFailed("Failed to get number of connected usb devices!")

            if usb_count != self.usb_count:
                raise RunFailed(
                    "Wrong number of usb devices '%d' != '%d'" % (usb_count, self.usb_count))
            self.progress.emit(100)
            return True


class miniPCIeTest(BaseTest):
    _name = 'miniPCIe'

    def __init__(self, pci_count):
        self.pci_count = pci_count

    def createWorker(self):
        return self.Worker(self.pci_count)

    class Worker(BaseWorker):

        def __init__(self, pci_count):
            super(miniPCIeTest.Worker, self).__init__()
            self.pci_count = pci_count

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(20)

            exp.sendline('echo "###$(cat /sys/bus/pci/devices/*/vendor | grep -c 0x168c)###"')

            pattern = r'###[0-9]+###'
            self.expect(exp, pattern)
            pci_count = exp.match.group()
            self.progress.emit(50)

            try:
                pci_count = int(pci_count.strip().strip("#"))
            except ValueError:
                raise RunFailed("Failed to get number of connected mPCIe devices!")

            if pci_count != self.pci_count:
                raise RunFailed(
                    "Wrong number of mPCIe devices '%d' != '%d'" % (pci_count, self.pci_count))
            self.progress.emit(100)
            return True


class SerialNumberTest(BaseTest):
    _name = 'SERIAL NUMBER'

    def createWorker(self):
        return self.Worker(qApp.router.idHex)

    class Worker(BaseWorker):

        def __init__(self, serial):
            super(SerialNumberTest.Worker, self).__init__()
            self.serial = serial

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(20)

            exp.sendline('atsha204cmd serial-number')
            pattern = r'[a-fA-F0-9]{16}'
            self.expect(exp, pattern)
            serial = exp.match.group()
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
            firmware = exp.match.group()
            self.progress.emit(80)

            self.expectLastRetval(exp, 0)
            self.progress.emit(90)

            self.firmware.emit(firmware)
            self.progress.emit(100)
            exp.terminate(force=True)
            return True


class ClockTest(BaseTest):
    _name = 'CLOCK'

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(20)

            exp.sendline('hwclock')
            pattern = r'[a-zA-z0-9\.\: ]* seconds'
            self.expect(exp, pattern)
            time = exp.match.group()
            # we need to switch locale to en_US.UTF-8 to correctly parse the date
            # note that setlocale and getlocale are not thread safe so don't use
            # it outside of this thread
            backup_locale = locale.getlocale(locale.LC_TIME)
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
            time = datetime.strptime(time, '%a %b %d %H:%M:%S %Y 0.%f seconds')
            locale.setlocale(locale.LC_TIME, backup_locale)
            self.progress.emit(50)

            # check whether the date diff matches +-1 day
            diff_seconds = (time - datetime.utcnow()).total_seconds()
            if math.fabs(diff_seconds) > 24 * 60 * 60:
                raise RunFailed(
                    "Router hwclock is too distant from the system time (%f seconds)"
                    % diff_seconds
                )

            self.progress.emit(100)
            return True


class MockTest(BaseTest):
    _name = "MOCK"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

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
    UsbTest(2),
    miniPCIeTest(3),
    SimpleTest("THERMOMETER", False),
    SimpleTest("GPIO", True),
    ClockTest(),
    SerialNumberTest(),
    MockTest(),
)
