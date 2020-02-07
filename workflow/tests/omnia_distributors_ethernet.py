# -*- coding: utf8 -*-

from workflow.tests.omnia import Booted
from workflow.tests.omnia_distributors import EthTest, DeviceTreeLink


class BootedEth(Booted):
    _name = 'BOOTED'

    @property
    def instructions(self):
        return """
            <h3>Kontrola síťových portů</h3>
            <ul>
                <li>Zkontrolujte, že máte do počítače připojený eth dongle.</li>
                <li>Zkontrolujte, máte do eth donglu připojený kabel.</li>
                <li>Připojte napájení k routeru.</li>
            <ul>
        """


class BootedSFP(Booted):
    _name = "BOOTED 2"

    @property
    def instructions(self):
        return """
            <h3>Druhý krok</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Vytáhněte napájení</li>
                <li>Odpojte Ethernet kabel(y)</li>
                <li>Připojte SFP modul do routeru.</li>
                <li>Připojte ethernetový kabel do SFP modulu.</li>
                <li>Připojte napájení</li>
            </ul>
        """


TESTS = (
    BootedEth(),
    EthTest("eth2", "ethTEST", "WAN", 167),
    EthTest("br-lan", "ethTEST", "LAN4", 166),
    EthTest("br-lan", "ethTEST", "LAN3", 165),
    EthTest("br-lan", "ethTEST", "LAN2", 164),
    EthTest("br-lan", "ethTEST", "LAN1", 163),
    EthTest("br-lan", "ethTEST", "LAN0", 162),
    DeviceTreeLink("sfp"),
    BootedSFP(),
    EthTest("eth2", "ethTEST", "WAN (SFP)", 161),
    DeviceTreeLink("phy"),
)
