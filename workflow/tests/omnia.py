# -*- coding: utf8 -*-

import locale
import math
import pexpect

from application import qApp, settings
from datetime import datetime
from workflow.base import Base, BaseTest, BaseWorker, spawnPexpectSerialConsole
from custom_exceptions import RunFailed


class UsbTest(BaseTest):

    def __init__(self, usb_count, name):
        self.usb_count = usb_count
        self._name = name

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


class MiniPCIeTest(BaseTest):
    _name = 'MINIPCIE'

    def __init__(self, pci_count):
        self.pci_count = pci_count

    def createWorker(self):
        return self.Worker(self.pci_count)

    class Worker(BaseWorker):

        def __init__(self, pci_count):
            super(MiniPCIeTest.Worker, self).__init__()
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


class GpioTest(BaseTest):
    _name = 'GPIO'

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):
        def testPins(self, exp, inputPins, outputPins, progressStart, progressEnd):
            pinLen = len(inputPins.split(" ")) + len(outputPins.split(" "))
            step = (progressEnd - progressStart) / 10.0
            # Set in and outs
            exp.sendline(
                'for i in %s; do '
                'echo in > /sys/class/gpio/gpio${i}/direction; '
                'done' % inputPins
            )
            self.progress.emit(progressStart + step * 1)
            self.expectLastRetval(exp, 0)
            self.progress.emit(progressStart + step * 2)
            exp.sendline(
                'for i in %s; do '
                'echo out > /sys/class/gpio/gpio${i}/direction; '
                'done' % outputPins
            )
            self.progress.emit(progressStart + step * 3)
            self.expectLastRetval(exp, 0)
            self.progress.emit(progressStart + step * 4)

            # Write values
            exp.sendline(
                'for i in %s; do '
                'echo 1 > /sys/class/gpio/gpio${i}/value; '
                'done' % outputPins
            )
            self.progress.emit(progressStart + step * 5)
            self.expectLastRetval(exp, 0)
            self.progress.emit(progressStart + step * 6)

            # Read values
            exp.sendline(
                'for i in %s %s; do '
                'cat /sys/class/gpio/gpio${i}/value; '
                'done' % (inputPins, outputPins)
            )
            self.expect(exp, r'1[\s]+' * (pinLen))
            self.progress.emit(progressStart + step * 7)

            # Write values
            exp.sendline(
                'for i in %s; do '
                'echo 0 > /sys/class/gpio/gpio${i}/value; '
                'done' % outputPins
            )
            self.progress.emit(progressStart + step * 8)
            self.expectLastRetval(exp, 0)
            self.progress.emit(progressStart + step * 9)

            # Read values
            exp.sendline(
                'for i in %s %s; do '
                'cat /sys/class/gpio/gpio${i}/value; '
                'done' % (inputPins, outputPins)
            )
            self.expect(exp, r'0[\s]+' * (pinLen))
            self.progress.emit(progressStart + step * 10)

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(3)

            pins1 = "18 34 36 44 51"
            pins2 = "33 35 42 47 56"

            # Init gpio ports
            exp.sendline(
                'for i in %s %s; do '
                'echo $i > /sys/class/gpio/export; '
                'done' % (pins1, pins2)
            )
            self.progress.emit(5)
            self.expectLastRetval(exp, 0)
            self.progress.emit(10)

            self.testPins(exp, pins1, pins2, 10, 55)
            self.testPins(exp, pins2, pins1, 55, 100)

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


class EthTest(BaseTest):
    localDev = "ethTEST"

    def __init__(self, device, socket, subnet, reinitDevice=False):
        self._name = "ETH %s" % socket
        self.device = device
        self.subnet = subnet
        self.socket = socket
        self.reinitDevice = reinitDevice

    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Připojte ethernetový kabel do zdířky %(socket)s</li>
            </ul>
        """ % dict(test_name=self._name, socket=self.socket)

    def createWorker(self):
        return self.Worker(self.device, self.subnet, self.reinitDevice)

    class Worker(BaseWorker):
        def __init__(self, device, subnet, reinitDevice):
            super(EthTest.Worker, self).__init__()
            self.device = device
            self.subnet = subnet
            self.reinitDevice = reinitDevice

        def perform(self):

            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)
            self.expectSystemConsole(exp)
            self.progress.emit(10)

            # initialize local device
            self.expectLocalCommand("sudo ip address flush dev %s" % EthTest.localDev)
            self.progress.emit(20)
            self.expectLocalCommand(
                "sudo ip address add 192.168.%d.1/24 dev %s" % (self.subnet, EthTest.localDev)
            )
            self.progress.emit(30)
            self.expectLocalCommand("sudo ip link set dev %s up" % EthTest.localDev)
            self.progress.emit(40)

            # reinit network if needed
            if self.reinitDevice:
                self.expectCommand(exp, "/etc/init.d/network restart")
                self.progress.emit(45)

            # set ip on router
            self.expectCommand(exp, "ip address flush dev %s" % self.device)
            self.progress.emit(50)
            self.expectCommand(
                exp, "ip address add 192.168.%d.10/24 dev %s" % (self.subnet, self.device)
            )
            self.progress.emit(60)
            self.expectCommand(exp, "ip link set dev %s up" % self.device)
            self.progress.emit(70)

            # ping test
            self.expectCommand(exp, "ping 192.168.%d.1 -c 5" % self.subnet)
            self.progress.emit(80)

            # local cleanup
            self.expectLocalCommand("sudo ip link set dev %s down" % EthTest.localDev)
            self.progress.emit(90)
            self.expectLocalCommand("sudo ip address flush dev %s" % EthTest.localDev)
            self.progress.emit(100)

            return True


class SerialConsoleTest(BaseTest):
    _name = "SERIAL CONSOLE"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)
            self.expectSystemConsole(exp)
            self.progress.emit(10)

            chars = ['^', '!', '+', '@']
            batches = [
                (500, 4),
                (100, 4),
                (20, 4),
                (1, 4),
            ]

            steps = sum([e[1] for e in batches])

            step = 1
            for size, count in batches:
                # generate string
                data = "".join(chars) * (count * (size + 1) / len(chars))
                for i in range(count):
                    line = data[i * size:(i + 1) * size]
                    exp.sendline('echo %s' % data)
                    self.expect(exp, "".join(["\\%s" % e for e in line]))
                    self.progress.emit(10 + step * (90.0 / steps))
                    step += 1

            return True


class Booted(Base):
    """
    Wait till router is booted in serial console
    It detects router stated and acts accordingly.

    Note that this is not actually a test -> run is aborted if it fails
    (no point to perform the tests when the router is not booted)
    """
    _name = "BOOTED 1"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):
        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            # determinate status
            exp.sendline("\n")
            res = self.expect(exp, [r'root@turris:/#', r'=>', pexpect.TIMEOUT], timeout=5)
            if res == 0:
                self.progress.emit(50)
                # Read while something is printed to the console
                # (booting is still in process, but the console is ready)
                while 0 == self.expect(exp, [r'.', pexpect.TIMEOUT], timeout=10):
                    pass
                # Booted and serial console ready
                self.progress.emit(100)
                return True

            elif res == 1:
                # In uboot -> try to boot
                exp.sendline("boot")
                self.progress.emit(10)
                booting_start = 10

            else:
                booting_start = 1

            self.expectWaitBooted(exp, booting_start, 100)

            return True


class Booted2(Booted):
    _name = "BOOTED 2"

    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Odpojte napájení routeru</li>
                <li>Odpojte eth kabely od routeru</li>
                <li>Připojte SPF ETH redukci</li>
                <li>Odpojte USB2 dongly z obou usb slotů</li>
                <li>Zapojte USB3 dongly do obou usb slotů</li>
                <li>Připojte napájení napájení do routeru.</li>
            </ul>
        """ % dict(test_name=self._name)

    def createWorker(self):
        return Booted.Worker()


class RamTest(BaseTest):
    """
    This test will try to test whether the router has flashed with given RAM size.

    Note that if this test fails, a 'BOOTED' test should be performed.
    So it is best to run this test as the last one.
    """
    _name = "RAM TEST"

    def createWorker(self):
        return self.Worker(settings.ROUTER_RAMSIZE)

    class Worker(BaseWorker):
        def __init__(self, ramsize):
            super(RamTest.Worker, self).__init__()
            # The only two valid options are `1` or `2`
            self.ramsize = ramsize

        def perform(self):
            if self.ramsize not in (1, 2, ):
                raise ValueError("Ramsize could be only '1' or '2' (%d given)" % self.ramsize)

            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])

            self.progress.emit(1)
            self.expectSystemConsole(exp)
            self.progress.emit(30)

            mountCmd = 'mount /tmp/ -o remount,size=%dk' % (1000 * 1000 * self.ramsize * 0.80)
            allocCmd = 'dd if=/dev/zero of=/tmp/ramtest.bin bs=1024 count=%d && ' \
                'echo "RAM" "TEST" "PASSED"' % (1000 * 1000 * self.ramsize * 0.75)

            # remount tmpfs
            exp.sendline(mountCmd)
            exp.sendline('\n')
            self.expectLastRetval(exp, 0)
            self.progress.emit(60)

            # try to allocate space on tmpfs
            exp.sendline(allocCmd)
            self.expect(exp, r'RAM TEST PASSED')

            self.progress.emit(90)
            self.ram.emit(self.ramsize, 'T')
            self.progress.emit(95)

            # a small cleanup
            exp.sendline("rm /tmp/ramtest.bin")
            exp.sendline('\n')
            self.expectLastRetval(exp, 0)

            self.progress.emit(100)

            return True


TESTS = (
    Booted(),
    SerialConsoleTest(),
    GpioTest(),
    UsbTest(2, "USB2"),
    MiniPCIeTest(3),
    ClockTest(),
    SerialNumberTest(),
    EthTest("eth1", "WAN", 167),
    EthTest("br-lan", "LAN1", 166),
    EthTest("br-lan", "LAN2", 165),
    Booted2(),
    UsbTest(2, "USB3"),
    EthTest("eth1", "WAN (SPF)", 164, True),
    RamTest(),
)
