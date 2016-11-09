# -*- coding: utf8 -*-

from workflow.tests.omnia import Booted, DiskTest


class BootedUsb(Booted):
    @property
    def instructions(self):
        return """
            <h3>Kontrola funkce USB portů</h3>
            <ul>
                <li>Ujistěte se, že máte 2xUSB2 a 2xUSB3 flash disky.</li>
                <li>Připojte napájení k routeru.</li>
            <ul>
        """


class Usb2Test(DiskTest):
    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Připoje dva USB2 flash disky do volných portů.</li>
            </ul>
        """ % dict(test_name=self._name)


class Usb3Test(DiskTest):
    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Odpojte USB2 flash disky.</li>
                <li>Připoje dva USB3 flash disky do volných portů.</li>
            </ul>
        """ % dict(test_name=self._name)


TESTS = (
    BootedUsb(),
    Usb2Test(2, "2xUSB2"),
    Usb3Test(2, "2xUSB3"),
)
