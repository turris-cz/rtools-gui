# coding=utf-8

# this file defines tests which are run after successful flashing
# it is a tuple of tests, each of which contains description for
# a person executing the tests and second is a function which takes
# SerialConsole object and executest the tests
# a test can yield -1 - unparsable command output
#                  >=0 - result of the test


import time

import os
import importlib
settings_module = os.environ.get('RTOOLS_SETTINGS', 'settings')
settings = importlib.import_module(settings_module)


def test_ETHERNET(sc):
    time.sleep(2)  # wait for link

    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.100.2" % settings.LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult

    cmdResult = runRemoteCmd(sc, "ifconfig br-wan 192.168.100.1")
    if cmdResult[0] != 0:
        return cmdResult

    time.sleep(1)  # wait for addresses to be set

    return runLocalCmd("ping -c 3 192.168.100.1")


from tests.common import runLocalCmd, runRemoteCmd, textresult_generic
from tests.turris import (
    test_serial_console,
    test_miniPCIe,
    test_GPIO,
    test_SPI,
    test_I2C,
    test_thermometer,
    test_hwclock,
    test_atshacmd,
    test_USB,
    textresult_miniPCIe,
    textresult_USB,
)


TESTLIST = (
    {
        "desc": u"test sériové konzole",
        "instructions": u"Připojte kabel č. 5 do konektoru J1.",
        "testfunc": test_serial_console,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test WAN portu",
        "instructions": u"Zapojte testovací ethernet kabel do portu WAN "
                        u"a počkejte, až se rozsvítí odpovídající dioda.",
        "testfunc": test_ETHERNET,
        "interpretfailure": textresult_generic,
        "interactive": True,
    },
    {
        "desc": u"test LAN portu č. 1",
        "instructions": u"Zapojte testovací ethernet kabel do portu LAN 1 "
                        u"a počkejte, až se rozsvítí odpovídající dioda.",
        "testfunc": test_ETHERNET,
        "interpretfailure": textresult_generic,
        "interactive": True,
    },
    {
        "desc": u"test LAN portu č. 2",
        "instructions": u"Zapojte testovací ethernet kabel do portu LAN 2 "
                        u"a počkejte, až se rozsvítí odpovídající dioda.",
        "testfunc": test_ETHERNET,
        "interpretfailure": textresult_generic,
        "interactive": True,
    },
    {
        "desc": u"test USB",
        "instructions": u"Zkontrolujte připojení USB klíčů.",
        "testfunc": test_USB,
        "interpretfailure": textresult_USB,
        "interactive": False,
    },
    {
        "desc": u"test mini PCI express slotů",
        "instructions": u"Zkontrolujte připojení mini PCIe karet.",
        "testfunc": test_miniPCIe,
        "interpretfailure": textresult_miniPCIe,
        "interactive": False,
    },
    {
        "desc": u"test GPIO",
        "instructions": u"Zkontrolujte připojení GPIO přípravku.",
        "testfunc": test_GPIO,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test SPI",
        "instructions": u"Zkontrolujte připojení I2C2, SPI, UART přípravku.",
        "testfunc": test_SPI,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test I2C",
        "instructions": u"Zkontrolujte připojení I2C2, SPI, UART přípravku.",
        "testfunc": test_I2C,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test příkazu hwclock",
        "instructions": u"Připojte kabel č. 5 do konektoru J1.",
        "testfunc": test_hwclock,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test příkazu thermometer",
        "instructions": u"Připojte kabel č. 5 do konektoru J1.",
        "testfunc": test_thermometer,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test příkazu atshacmd",
        "instructions": u"Připojte kabel č. 5 do konektoru J1.",
        "testfunc": test_atshacmd,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
)
