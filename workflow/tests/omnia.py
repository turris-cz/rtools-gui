# -*- coding: utf8 -*-

import binascii
import locale
import math
import pexpect
import re

from application import qApp, settings
from datetime import datetime
from workflow.base import Base, BaseTest, BaseWorker, spawnPexpectSerialConsole
from custom_exceptions import RunFailed


class DiskTest(BaseTest):

    def __init__(self, usb_count, name):
        self.usb_count = usb_count
        self._name = "DISK %s" % name

    def createWorker(self):
        return self.Worker(self.usb_count)

    class Worker(BaseWorker):

        def __init__(self, usb_count):
            super(DiskTest.Worker, self).__init__()
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

    def __init__(self, pci_count, name):
        self.pci_count = pci_count
        self._name = "MINIPCIE %s" % name

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

            # remove wifi configs
            self.expectCommand(exp, "rm -rf /etc/config/wireless")
            self.expectCommand(exp, "sync")

            # this will print which pci slots are available into the console
            self.expectCommand(exp, "grep -i -e 0x168c /sys/bus/pci/devices/*/vendor || true")

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

            retries = 2  # try to retry 2 times
            serial = 0
            while True:
                exp.sendline('atsha204cmd serial-number')
                pattern = r'[a-fA-F0-9]{16}'
                res = self.expect(exp, [pattern, pexpect.TIMEOUT], timeout=5)
                if res == 0:
                    serial = exp.match.group()
                    self.progress.emit(40)

                    self.expectLastRetval(exp, 0)
                    self.progress.emit(50)
                    break
                else:
                    retries -= 1
                    if retries < 0:
                        raise RunFailed("Failed to get serial number!")

            if self.serial.lower() != serial.lower():
                exp.terminate(force=True)
                raise RunFailed("Serial number doesn't match '%s' != '%s'" % (self.serial, serial))

            # try storing the firmware if the serial matches
            exp.sendline('cat /etc/git-version')
            pattern = r'[a-fA-F0-9]{40}'
            self.expect(exp, pattern)
            firmware = exp.match.group()
            self.progress.emit(70)

            self.expectLastRetval(exp, 0)
            self.progress.emit(80)

            # read eeprom and store it
            devicePath = '/sys/devices/platform/soc/soc:internal-regs/f1011000.i2c/i2c-0/i2c-1/1-0054/eeprom'
            exp.sendline("hexdump %s | head -n 1 | cut -d' ' -f2-" % devicePath)
            pattern = " ".join([r'[a-fA-F0-9]{4}'] * 8)
            self.expect(exp, pattern)
            eeprom = exp.match.group()
            self.progress.emit(90)

            self.expectLastRetval(exp, 0)
            self.progress.emit(100)

            self.firmware.emit(firmware)
            self.eeprom.emit(eeprom, 'T')

            exp.terminate(force=True)
            return True


class EepromTest(BaseTest):
    _name = 'EEPROM TEST'

    def createWorker(self):
        return self.Worker(settings.ROUTER_RAMSIZE, settings.REGION)

    class Worker(BaseWorker):
        def __init__(self, ramsize, region):
            super(EepromTest.Worker, self).__init__()
            self.ramsize = ramsize
            self.region = region

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(40)

            devicePath = '/sys/devices/platform/soc/soc:internal-regs/f1011000.i2c/i2c-0/i2c-1/1-0054/eeprom'
            exp.sendline("hexdump %s | head -n 1 | cut -d' ' -f2-" % devicePath)
            pattern = " ".join([r'[a-fA-F0-9]{4}'] * 8)
            self.expect(exp, pattern)
            eeprom = exp.match.group().split(" ")
            storedRam = int(eeprom[2], 16)
            storedRegion = binascii.unhexlify(eeprom[4])[::-1]  # it is reversed
            self.progress.emit(95)

            errors = []
            if storedRam != self.ramsize:
                errors.append("Ramsize mismatch (%dG!=%dG)" % (self.ramsize, storedRam))
            if storedRegion != self.region:
                errors.append("Region mismatch ('%s'!='%s')" % (self.region, storedRegion))

            if errors:
                exp.terminate(force=True)
                raise RunFailed(", ".join(errors))

            self.progress.emit(100)

            # TODO parse and check

            return True


class RegionTest(BaseTest):
    _name = 'REGION TEST'

    def createWorker(self):
        return self.Worker(settings.REGION)

    class Worker(BaseWorker):
        def __init__(self, region):
            super(RegionTest.Worker, self).__init__()
            self.region = region

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(40)

            exp.sendline("echo '>''>>'$(cat /proc/cmdline)'<<<'")
            self.expect(exp, r'^.*>>>(.*)<<<.*$')
            cmdline = exp.match.group(1)

            match = re.match(r'.*cfg80211.freg=(..).*', cmdline)
            if not match:
                exp.terminate(force=True)
                raise RunFailed("Could not read region from the kernel command line")
            elif match.group(1) != self.region:
                exp.terminate(force=True)
                raise RunFailed(
                    "Region from the kernel commandline differs. ('%s'!='%s')"
                    % (self.region, match.group(1))
                )

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

    def __init__(self, routerDev, localDev, socket, subnet, reinitDevice=False):
        self._name = "ETH %s" % socket
        self.routerDev = routerDev
        self.localDev = localDev
        self.subnet = subnet
        self.socket = socket
        self.reinitDevice = reinitDevice

    # @property
    # def instructions(self):
    #     return """
    #         <h3>%(test_name)s</h3>
    #         <p>Před tím, než budete pokračovat:</p>
    #         <ul>
    #             <li>Připojte ethernetový kabel do zdířky %(socket)s</li>
    #         </ul>
    #     """ % dict(test_name=self._name, socket=self.socket)

    def createWorker(self):
        return self.Worker(self.routerDev, self.localDev, self.subnet, self.reinitDevice)

    class Worker(BaseWorker):
        def __init__(self, routerDev, localDev, subnet, reinitDevice):
            super(EthTest.Worker, self).__init__()
            self.routerDev = routerDev
            self.localDev = localDev
            self.subnet = subnet
            self.reinitDevice = reinitDevice

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)
            self.expectSystemConsole(exp)
            self.progress.emit(10)

            # initialize local device
            self.expectLocalCommand("sudo ip address flush dev %s" % self.localDev)
            self.progress.emit(20)
            self.expectLocalCommand(
                "sudo ip address add 192.168.%d.1/24 dev %s" % (self.subnet, self.localDev)
            )
            self.progress.emit(30)
            self.expectLocalCommand("sudo ip link set dev %s up" % self.localDev)
            self.progress.emit(40)

            # reinit network if needed
            if self.reinitDevice:
                self.expectCommand(exp, "/etc/init.d/network restart")
                self.progress.emit(45)

            # set ip on router
            self.expectCommand(exp, "ip address flush dev %s" % self.routerDev)
            self.progress.emit(50)
            self.expectCommand(
                exp, "ip address add 192.168.%d.10/24 dev %s" % (self.subnet, self.routerDev)
            )
            self.progress.emit(60)
            self.expectCommand(exp, "ip link set dev %s up" % self.routerDev)
            self.progress.emit(70)

            # ping test
            exp.sendline("ping 192.168.%d.1 -c 5" % self.subnet)
            exp.sendline('echo "###$?###"')
            self.expect(exp, r'###([0-9]+)###')
            retval = exp.match.group(1)
            self.progress.emit(80)

            # local cleanup
            self.expectLocalCommand("sudo ip link set dev %s down" % self.localDev)
            self.progress.emit(90)
            self.expectLocalCommand("sudo ip address flush dev %s" % self.localDev)
            self.progress.emit(100)

            if retval != "0":
                raise RunFailed("Ping failed!")

            return True


class EthSimpleTest(BaseTest):

    def __init__(self, routerDev, socket, subnet):
        self._name = "ETH %s" % socket
        self.routerDev = routerDev
        self.subnet = subnet
        self.socket = socket

    def createWorker(self):
        return self.Worker(self.routerDev, self.subnet)

    class Worker(BaseWorker):
        def __init__(self, routerDev, subnet):
            super(EthSimpleTest.Worker, self).__init__()
            self.routerDev = routerDev
            self.subnet = subnet

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)
            self.expectSystemConsole(exp)
            self.progress.emit(20)

            # set ip on router
            self.expectCommand(exp, "ip address flush dev %s" % self.routerDev)
            self.progress.emit(40)
            self.expectCommand(
                exp, "ip address add 192.168.%d.10/24 dev %s" % (self.subnet, self.routerDev)
            )
            self.progress.emit(60)
            self.expectCommand(exp, "ip link set dev %s up" % self.routerDev)
            self.progress.emit(80)

            # ping test
            exp.sendline("ping 192.168.%d.1 -c 5" % self.subnet)
            exp.sendline('echo "###$?###"')
            self.expect(exp, r'###([0-9]+)###')
            retval = exp.match.group(1)
            self.progress.emit(100)

            if retval != "0":
                raise RunFailed("Ping failed!")

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

    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Připojte WAN, LAN1 a LAN2 eth kabely k routeru.</li>
                <li>Připojte 3 mPCI wifi karty do 3 slotů na desce.</li>
                <li>Připojte GPIO testovací zařízení k desce.</li>
                <li>Připojte UART kabel k routeru.</li>
                <li>Zapojte USB2 dongly do obou usb slotů</li>
                <li>Připojte napájení napájení do routeru.</li>
            </ul>
        """ % dict(test_name=self._name)

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
                <li>Připojte SFP ETH redukci k routeru</li>
                <li>Připojte WAN do SFP ETH redukce</li>
                <li>Odpojte USB2 dongly z obou usb slotů</li>
                <li>Zapojte USB3 dongly do obou usb slotů</li>
                <li>Odpojte zařízení z mPCI slotu nejblíže ke středu desky</li>
                <li>Zapojte mSata kartu do mPCI slotu nejblíže ke středu desky</li>
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

            # remove ssh configs
            self.expectCommand(exp, "rm -rf /etc/ssh/ssh_host*")
            self.expectCommand(exp, "sync")

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
    DiskTest(2, "2xUSB2"),
    MiniPCIeTest(3, "3xPCI"),
    ClockTest(),
    SerialNumberTest(),
    EepromTest(),
    RegionTest(),
    #EthTest("eth1", "ethWAN", "WAN", 167),
    #EthTest("br-lan", "ethLAN1", "LAN1", 166),
    #EthTest("br-lan", "ethLAN2", "LAN2", 165),
    EthSimpleTest("eth1", "WAN", 168),
    EthSimpleTest("br-lan", "LAN1", 167),
    EthSimpleTest("br-lan", "LAN2", 166),
    EthSimpleTest("br-lan", "LAN3", 165),
    EthSimpleTest("br-lan", "LAN4", 164),
    EthSimpleTest("br-lan", "LAN5", 163),
    Booted2(),
    DiskTest(3, "2xUSB3+MSATA"),
    MiniPCIeTest(2, "2xPCI"),
    #EthTest("eth1", "ethWAN", "WAN (SFP)", 162),
    EthSimpleTest("eth1", "WAN (SFP)", 168),
    RamTest(),
)
