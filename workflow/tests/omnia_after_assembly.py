# -*- coding: utf8 -*-

from workflow.tests.omnia import (
    Booted, SerialNumberTest, MiniPCIeTest, ClockTest
)


class BootedMod(Booted):
    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Připojte UART kabel k routeru.</li>
                <li>Připojte napájení napájení do routeru.</li>
            </ul>
        """ % dict(test_name=self._name)


TESTS = (
    BootedMod(),
    SerialNumberTest(),
    MiniPCIeTest("3-01", 0x01),
    MiniPCIeTest("3-02", 0x02),
    ClockTest(),
)
