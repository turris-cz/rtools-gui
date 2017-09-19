# -*- coding: utf8 -*-

from workflow.tests.omnia import (
    TESTS as ORIG_TESTS, GpioTest, Booted, Booted2
)


class Booted1Gpio(Booted):

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


TESTS = [
    Booted1Gpio() if isinstance(e, Booted) and not isinstance(e, Booted2) else e
    for e in ORIG_TESTS if not isinstance(e, GpioTest)
]
