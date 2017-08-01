# -*- coding: utf8 -*-

from application import settings
from custom_exceptions import RunFailed
from workflow.base import BaseTest, BaseWorker, spawnPexpectSerialConsole
from workflow.tests.omnia import (
    Booted, Booted2, SerialConsoleTest, GpioTest, DiskTest, ClockTest,
    SerialNumberTest, EepromTest, RegionTest, MiniPCIeTest, MSATATest, RamTest, USBTest
)


class EthTest(BaseTest):

    def __init__(self, routerDev, localDev, socket, subnet, reinitDevice=False):
        self._name = "ETH %s" % socket
        self.routerDev = routerDev
        self.localDev = localDev
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


class BootedMod(Booted):
    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Připojte eth kabel k WAN portu routeru.</li>
                <li>Připojte 3 mPCI wifi karty do 3 slotů na desce.</li>
                <li>Připojte GPIO testovací zařízení k desce.</li>
                <li>Připojte UART kabel k routeru.</li>
                <li>Zapojte USB2 dongly do obou usb slotů</li>
                <li>Připojte napájení napájení do routeru.</li>
            </ul>
        """ % dict(test_name=self._name)


class Booted2Mod(Booted2):
    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Odpojte napájení routeru</li>
                <li>Odpojte eth kabel od routeru</li>
                <li>Připojte SFP ETH redukci k routeru</li>
                <li>Připojte eth kabel k do SFP ETH redukce</li>
                <li>Odpojte USB2 dongly z obou usb slotů</li>
                <li>Zapojte USB3 dongly do obou usb slotů</li>
                <li>Odpojte zařízení z mPCI slotu nejblíže ke středu desky</li>
                <li>Zapojte mSata kartu do mPCI slotu nejblíže ke středu desky</li>
                <li>Připojte napájení napájení do routeru.</li>
            </ul>
        """ % dict(test_name=self._name)


TESTS = (
    BootedMod(),
    SerialConsoleTest(),
    GpioTest(),
    USBTest("2.0-1", "2-1", USBTest.USB2),
    USBTest("2.0-2", "4-1", USBTest.USB2),
    DiskTest(2, "2xUSB2"),
    MiniPCIeTest("1-01", 0x01),
    MiniPCIeTest("1-02", 0x02),
    MiniPCIeTest("1-03", 0x03),
    ClockTest(),
    SerialNumberTest(),
    EepromTest(),
    RegionTest(),
    EthTest("eth1", "ethTEST", "WAN", 167),
    EthTest("br-lan", "ethTEST", "LAN4", 166),
    EthTest("br-lan", "ethTEST", "LAN3", 165),
    EthTest("br-lan", "ethTEST", "LAN2", 164),
    EthTest("br-lan", "ethTEST", "LAN1", 163),
    EthTest("br-lan", "ethTEST", "LAN0", 162),
    Booted2Mod(),
    USBTest("3.0-1", "3-1", USBTest.USB3),
    USBTest("3.0-2", "5-1", USBTest.USB3),
    MSATATest(),
    DiskTest(3, "2xUSB3+MSATA"),
    MiniPCIeTest("2-02", 0x02),
    MiniPCIeTest("2-03", 0x03),
    EthTest("eth1", "ethTEST", "WAN (SFP)", 161),
    RamTest(),
)
