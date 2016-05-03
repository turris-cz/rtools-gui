# -*- coding: utf8 -*-

import locale
import math
import time

from application import qApp, settings
from datetime import datetime
from workflow.base import BaseTest, BaseWorker, spawnPexpectSerialConsole
from custom_exceptions import RunFailed


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


class EthTest(BaseTest):
    localDev = "ethTEST"

    def __init__(self, device, socket, subnet):
        self._name = "ETH %s" % socket
        self.device = device
        self.subnet = subnet
        self.socket = socket

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
        return self.Worker(self.device, self.subnet)

    class Worker(BaseWorker):
        def __init__(self, device, subnet):
            super(EthTest.Worker, self).__init__()
            self.device = device
            self.subnet = subnet

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


TESTS = (
    SerialConsoleTest(),
    UsbTest(2),
    miniPCIeTest(3),
    ClockTest(),
    SerialNumberTest(),
    EthTest("eth1", "WAN", 167),
    EthTest("br-lan", "LAN1", 166),
    EthTest("br-lan", "LAN2", 165),
)
