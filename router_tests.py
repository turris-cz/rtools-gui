# coding=utf-8

# this file defines tests which are run after successful flashing
# it is a tuple of tests, each of which contains description for
# a person executing the tests and second is a function which takes
# SerialConsole object and executest the tests
# a test can yield -2 - meaning 'something went wrong in software'
#                  -1 - meaning 'check the cable'
#                  >=0 - result of the test


import subprocess
from shlex import split


def runLocalCmd(cmdstr):
    p = subprocess.Popen(split(cmdstr), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    retCode = p.wait()
    stdOut = p.stdout.read().strip()
    return (retCode, stdOut)


def test_WAN(sc):
    print runLocalCmd("sudo ifconfig eth0 192.168.100.2")
    print sc.exec_("ifconfig eth2 192.168.100.1")
    return runLocalCmd("ping -c 3 192.168.100.1")[0]


def test_LAN1(sc):
    runLocalCmd("sudo ifconfig eth0 192.168.1.2")
    return runLocalCmd("ping -c 3 192.168.1.1")[0]


def test_LAN2345(sc):
    return runLocalCmd("ping -c 3 192.168.1.1")[0]


def test_USB1(sc):
    sc.exec_("[ -d /sys/bus/usb/devices/1-1.1/ ] && [ -b /dev/sda ]")
    retStat = sc.exec_("echo $?")
    if len(retStat) == 1:
        try:
            return int(retStat)
        except ValueError:
            return 1000
    
    # if output doesn't contain only the result, but also some other text, try it again
    sc.exec_("[ -d /sys/bus/usb/devices/1-1.1/ ] && [ -b /dev/sda ]")
    retStat = sc.exec_("echo $?")
    try:
        return int(retStat)
    except ValueError:
        return 1000


def test_USB2(sc):
    sc.exec_("[ -d /sys/bus/usb/devices/1-1.2/ ] && [ -b /dev/sda ]")
    retStat = sc.exec_("echo $?")
    if len(retStat) == 1:
        try:
            return int(retStat)
        except ValueError:
            return 1000
    
    # if output doesn't contain only the result, but also some other text, try it again
    sc.exec_("[ -d /sys/bus/usb/devices/1-1.2/ ] && [ -b /dev/sda ]")
    retStat = sc.exec_("echo $?")
    try:
        return int(retStat)
    except ValueError:
        return 1000


def test_miniPCIe(sc):
    retStr = sc.exec_("cat /sys/bus/pci/devices/*/vendor | grep -c '0x168c'")
    try:
        countPci = int(retStr)
        return 0 if countPci == 2 else -countPci
    except ValueError:
        return 1000


TESTLIST = (
{
    "desc":
        u"WAN test",
    "testfunc": test_WAN
},
{
    "desc":
        u"LAN1 test",
    "testfunc": test_LAN1
},
{
    "desc":
        u"LAN2 test",
    "testfunc": test_LAN2345
},
{
    "desc":
        u"LAN3 test",
    "testfunc": test_LAN2345
},
{
    "desc":
        u"LAN4 test",
    "testfunc": test_LAN2345
},
{
    "desc":
        u"USB1 test",
    "testfunc": test_USB1
},
{
    "desc":
        u"USB2 test",
    "testfunc": test_USB2
},
{
    "desc":
        u"mini PCIe test",
    "testfunc": test_miniPCIe
},
)
