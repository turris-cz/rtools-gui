# -*- coding: utf8 -*-

from workflow.tests.omnia import Booted, MiniPCIeTest, MSATATest


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
    MSATATest(),
    MiniPCIeTest("2-02", 0x02),
    MiniPCIeTest("2-03", 0x03),
    BootedMpci2(),
    MiniPCIeTest("1-01", 0x01),
    MiniPCIeTest("1-02", 0x02),
    MiniPCIeTest("1-03", 0x03),
)
