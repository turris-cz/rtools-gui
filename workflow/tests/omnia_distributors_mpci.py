# -*- coding: utf8 -*-

from workflow.tests.omnia import Booted, DiskTest, MiniPCIeTest


class BootedMpci1(Booted):
    _name = 'BOOTED MPCI 1'

    @property
    def instructions(self):
        return """
            <h3>Kontrola funkce miniPCI slotů</h3>
            <ul>
                <li>Ujistěte se, že je router odpojen od napájení.</li>
                <li>Zkontrolujte, že k routeru není připojeno žádné USB zařízení.</li>
                <li>Vložte mSATA kartu do slotu 1</li>
                <li>Připojte mPCI wifi kartu do slotu 2</li>
                <li>Připojte mPCI wifi kartu do slotu 3</li>
                <li>Připojte napájení do routeru.</li>
            <ul>
        """


class BootedMpci2(Booted):
    _name = 'BOOTED MPCI 2'

    @property
    def instructions(self):
        return """
            <h3>Kontrola funkce miniPCI slotů</h3>
            <ul>
                <li>Odpojte napájení routeru</li>
                <li>Vyndejte mSATA kartu ze slotu 1</li>
                <li>Připojte mPCI wifi kartu do slotu 1</li>
                <li>Připojte napájení do routeru.</li>
            <ul>
        """

TESTS = (
    BootedMpci1(),
    DiskTest(1, "MSATA"),
    MiniPCIeTest(2, "2xPCI"),
    BootedMpci2(),
    MiniPCIeTest(3, "3xPCI"),
)
