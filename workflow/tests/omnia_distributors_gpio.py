# -*- coding: utf8 -*-

from workflow.tests.omnia import Booted, GpioTest


class BootedGpio(Booted):
    _name = 'BOOTED GPIO'

    @property
    def instructions(self):
        return """
            <h3>Kontrola funkce miniPCI slotů</h3>
            <ul>
                <li>Ujistěte se, že je router odpojen od napájení.</li>
                <li>Připojte testovací přípravek do rozšiřujícího konektoru.</li>
                <li>Připojte napájení do routeru.</li>
            <ul>
        """

TESTS = (
    BootedGpio(),
    GpioTest(),
)
