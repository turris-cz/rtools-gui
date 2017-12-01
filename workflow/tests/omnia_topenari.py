# -*- coding: utf8 -*-

from workflow.tests.omnia import (
    Booted, Booted2
)

from workflow.tests.omnia import (
    SerialConsoleTest,
    USBTest,
    DiskTest,
    MiniPCIeTest,
    ClockTest,
    LedTest,
    ResetLed,
    EthSimpleTest,
    EepromTest,
    SerialNumberTest,
    RegionTest,
    RamTest,
)


class Booted1Topenari(Booted):

    @property
    def instructions(self):
        return """
            <h3>První krok</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Vytáhněte napájení (pokud je zapojeno)</li>
                <li>Připojte 1x WAN a 5x LAN kabely</li>
                <li>Připojte 3 miniPCI wifi karty (velké)</li>
                <li>Připojte 2x USB 2.0 flashky</li>
                <li>Připojte UART kabel</li>
                <li>Připojte napájení</li>
            </ul>
        """


class Booted2Topenari(Booted2):

    @property
    def instructions(self):
        return """
            <h3>První krok</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Vytáhněte napájení</li>
                <li>Odpojte 2x USB 2.0 flashky</li>
                <li>Odpojte miniPCI wifi kartu nejblíže k okraji</li>
                <li>Připojte miniPCI-USB redukci s USB 2.0 flashkou do slotu nejblíže k okraji</li>
                <li>Připojte 2x USB 3.0 flashky</li>
                <li>Připojte napájení</li>
            </ul>
        """


TESTS = (
    Booted1Topenari(),
    SerialConsoleTest(),
    USBTest("2.0-1", "2-1", USBTest.USB2),
    USBTest("2.0-2", "4-1", USBTest.USB2),
    DiskTest(2, "2x"),
    MiniPCIeTest("1-01", 0x01),
    MiniPCIeTest("1-02", 0x02),
    MiniPCIeTest("1-03", 0x03),
    ClockTest(),
    EthSimpleTest("eth1", "WAN", 168),
    EthSimpleTest("br-lan", "LAN1", 167),
    EthSimpleTest("br-lan", "LAN2", 166),
    EthSimpleTest("br-lan", "LAN3", 165),
    EthSimpleTest("br-lan", "LAN4", 164),
    EthSimpleTest("br-lan", "LAN5", 163),
    LedTest("red", u"červená"),
    LedTest("green", u"zelená"),
    LedTest("blue", u"modrá"),
    ResetLed(),
    Booted2Topenari(),
    USBTest("3.0-1", "3-1", USBTest.USB3),
    USBTest("3.0-2", "5-1", USBTest.USB3),
    USBTest("2.0-3", "1-1", USBTest.USB2),
    DiskTest(3, "3x"),
    MiniPCIeTest("1-01", 0x01),
    MiniPCIeTest("1-02", 0x02),
    EepromTest(),
    RegionTest(),
    SerialNumberTest(),
    RamTest(),
)
