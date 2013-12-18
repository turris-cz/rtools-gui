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


LOCAL_TEST_IFACE = "eth0"
TURRIS_WAN_IFACE = "eth2"


def runLocalCmd(cmdstr):
    p = subprocess.Popen(split(cmdstr), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    retCode = p.wait()
    stdOut = p.stdout.read().strip()
    return (retCode,
            "on local machine `" + cmdstr + "` returned:\n"
             + stdOut)


def runRemoteCmd(sc, cmdstr):
    stdOut = sc.exec_(cmdstr)
    cmdStatus = sc.lastStatus()
    try:
        cmdStatus = int(cmdStatus)
    except ValueError:
        cmdStatus = 1
    
    return (cmdStatus,
            "on tested turris `" + cmdstr + "` returned:\n"
            + stdOut + "\n-----\ncommand exit code: " + str(cmdStatus))


def test_WAN(sc):
    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.100.2" % LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult
    
    cmdResult = runRemoteCmd(sc, "ifconfig %s 192.168.100.1" % TURRIS_WAN_IFACE)
    if cmdResult[0] != 0:
        return cmdResult
    
    return runLocalCmd("ping -c 3 192.168.100.1")


def test_LAN1(sc):
    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.1.2" % LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult
    
    return test_LAN_ping(sc)


def test_LAN_ping(sc):
    return runLocalCmd("ping -c 3 192.168.1.1")


def test_USB1(sc):
    return runRemoteCmd(sc, "[ -d /sys/bus/usb/devices/1-1.1/ ] && [ -b /dev/sda ]")


def test_USB2(sc):
    return runRemoteCmd(sc, "[ -d /sys/bus/usb/devices/1-1.2/ ] && [ -b /dev/sda ]")


def test_miniPCIe(sc):
    cmd = "cat /sys/bus/pci/devices/*/vendor | grep -c '0x168c'"
    countPci = sc.exec_(cmd)
    try:
        countPci = int(countPci)
    except ValueError:
        return (1, "on tested turris `" + cmd + "` returned:\n" + str(countPci))
    else:
        if countPci == 2:
            return (0, "")
        else:
            return (1, "on tested turris `" + cmd + "` returned:\n" + str(countPci))


def test_GPIO(sc):
    funcdef = """
gpiotest () {
    GPIOS="$(seq 224 230) 239"
    for i in $GPIOS
    do
        if [ ! -e /sys/class/gpio/gpio$i ]
        then
            echo $i > /sys/class/gpio/export
        fi
    done
    GPIO_OUT="224 225 226 227"
    GPIO_IN="228 229 230 239"
    for i in $GPIO_OUT; do echo out > /sys/class/gpio/gpio$i/direction; done
    for i in $GPIO_IN; do echo in > /sys/class/gpio/gpio$i/direction; done

    for i in `seq 1 4`; do
        VAL=$(($i%2));
        echo $VAL > /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value;
        sleep 1
        OUTVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value`;
        INVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_IN | cut -d ' ' -f $i)/value`;
        if [ $OUTVAL -ne $INVAL ]
        then
            echo "error \$OUTVAL=$OUTVAL, \$INVAL=$INVAL, \$i=$i in the first stage"
            return 1
        fi
    done
    for i in `seq 1 4`; do
        VAL=$(($i%2));
        if [ $VAL -eq 0 ]; then VAL=1; else VAL=0; fi
        echo $VAL > /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value;
        sleep 1
        OUTVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value`;
        INVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_IN | cut -d ' ' -f $i)/value`;
        if [ $OUTVAL -ne $INVAL ]
        then
            echo "error \$OUTVAL=$OUTVAL, \$INVAL=$INVAL, \$i=$i in the second stage"
            return 1
        fi
    done

    GPIO_IN="224 225 226 227"
    GPIO_OUT="228 229 230 239"
    for i in $GPIO_OUT; do echo out > /sys/class/gpio/gpio$i/direction; done
    for i in $GPIO_IN; do echo in > /sys/class/gpio/gpio$i/direction; done

    for i in `seq 1 4`; do
        VAL=$(($i%2));
        echo $VAL > /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value;
        sleep 1
        OUTVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value`;
        INVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_IN | cut -d ' ' -f $i)/value`;
        if [ $OUTVAL -ne $INVAL ]
        then
            echo "error: \$OUTVAL=$OUTVAL, \$INVAL=$INVAL, \$i=$i in the third stage"
            return 1
        fi
    done
    for i in `seq 1 4`; do
        VAL=$(($i%2));
        if [ $VAL -eq 0 ]; then VAL=1; else VAL=0; fi
        echo $VAL > /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value;
        sleep 1
        OUTVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value`;
        INVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_IN | cut -d ' ' -f $i)/value`;
        if [ $OUTVAL -ne $INVAL ]
        then
            echo "error: \$OUTVAL=$OUTVAL, \$INVAL=$INVAL, \$i=$i in the fourth stage"
            return 1
        fi
    done
}
"""
    sc.exec_(funcdef)
    return runRemoteCmd(sc, "( set -e; gpiotest )")


TESTLIST = (
{
    "desc":
        u"test WAN portu",
    "testfunc": test_WAN
},
{
    "desc":
        u"test LAN portu č. 1",
    "testfunc": test_LAN1
},
{
    "desc":
        u"test LAN portu č. 2",
    "testfunc": test_LAN_ping
},
{
    "desc":
        u"test LAN portu č. 3",
    "testfunc": test_LAN_ping
},
{
    "desc":
        u"test LAN portu č. 4",
    "testfunc": test_LAN_ping
},
{
    "desc":
        u"test LAN portu č. 5",
    "testfunc": test_LAN_ping
},
{
    "desc":
        u"test USB č. 1",
    "testfunc": test_USB1
},
{
    "desc":
        u"test USB č. 2",
    "testfunc": test_USB2
},
{
    "desc":
        u"test mini PCI express slotů",
    "testfunc": test_miniPCIe
},
{
    "desc":
        u"test GPIO",
    "testfunc": test_GPIO
},
)
