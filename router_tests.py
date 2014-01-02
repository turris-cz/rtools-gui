# coding=utf-8

# this file defines tests which are run after successful flashing
# it is a tuple of tests, each of which contains description for
# a person executing the tests and second is a function which takes
# SerialConsole object and executest the tests
# a test can yield -2 - meaning 'something went wrong in software'
#                  -1 - meaning 'check the cable'
#                  >=0 - result of the test


import subprocess
import time
from shlex import split


LOCAL_TEST_IFACE = "eth42"
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
        cmdStatusInt = int(cmdStatus)
    except ValueError:
        cmdStatusInt = 1000
    
    return (cmdStatusInt,
            "on tested turris `" + cmdstr + "` returned:\n"
            + stdOut + "\n-----\ncommand exit code: " + cmdStatus)


def test_WAN(sc):
    time.sleep(2) # wait for link
    
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
    time.sleep(2) # wait for link
    return runLocalCmd("ping -c 3 192.168.1.1")


def test_USB(sc):
    cmd = "ls /dev/sd? 2> /dev/null | wc -l"
    countSD = sc.exec_(cmd)
    
    try:
        countSD = int(countSD)
    except ValueError:
        return (1000, "on tested turris `" + cmd + "` returned:\n" + str(countSD))
    else:
        if countSD == 2:
            return (0, "")
        else:
            return (1, "on tested turris `" + cmd + "` returned:\n" + str(countSD))


def test_miniPCIe(sc):
    cmd = "cat /sys/bus/pci/devices/*/vendor | grep -c '0x168c'"
    countPci = sc.exec_(cmd)
    try:
        countPci = int(countPci)
    except ValueError:
        return (1000, "on tested turris `" + cmd + "` returned:\n" + str(countPci))
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

    for i in 1 2 4; do
        VAL=$(($i%2));
        echo $VAL > /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value;
        OUTVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value`;
        INVAL=`cat /sys/class/gpio/gpio$(echo $GPIO_IN | cut -d ' ' -f $i)/value`;
        if [ $OUTVAL -ne $INVAL ]
        then
            echo "error: \$OUTVAL=$OUTVAL, \$INVAL=$INVAL, \$i=$i in the third stage"
            return 1
        fi
    done
    for i in 1 2 4; do
        VAL=$(($i%2));
        if [ $VAL -eq 0 ]; then VAL=1; else VAL=0; fi
        echo $VAL > /sys/class/gpio/gpio$(echo $GPIO_OUT | cut -d ' ' -f $i)/value;
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


def textresult_WAN(p_result):
    if p_result[0] == 0:
        return u"Test WAN portu proběhl úspěšně."
    else:
        return u"Při testování WAN portu nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


def textresult_LAN1(p_result):
    if p_result[0] == 0:
        return u"Test LAN portu č.1 proběhl úspěšně."
    else:
        return u"Při testování LAN portu č.1 nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


def textresult_LAN2(p_result):
    if p_result[0] == 0:
        return u"Test LAN portu č.2 proběhl úspěšně."
    else:
        return u"Při testování LAN portu č.2 nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


def textresult_LAN3(p_result):
    if p_result[0] == 0:
        return u"Test LAN portu č.3 proběhl úspěšně."
    else:
        return u"Při testování LAN portu č.3 nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


def textresult_LAN4(p_result):
    if p_result[0] == 0:
        return u"Test LAN portu č.4 proběhl úspěšně."
    else:
        return u"Při testování LAN portu č.4 nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


def textresult_LAN5(p_result):
    if p_result[0] == 0:
        return u"Test LAN portu č.5 proběhl úspěšně."
    else:
        return u"Při testování LAN portu č.5 nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


def textresult_USB(p_result):
    if p_result[0] == 0:
        return u"Test USB proběhl úspěšně."
    else:
        numdetected = p_result[1].split("` returned:\n")[-1]
        return u"Detekovali jsme jenom %s USB zařízení. Očekávali jsme 2." \
                % numdetected


def textresult_miniPCIe(p_result):
    if p_result[0] == 0:
        return u"Test mini PCI express proběhl úspěšně."
    else:
        numdetected = p_result[1].split("` returned:\n")[-1]
        return u"Detekovali jsme jenom %s mini PCI express slotů. Očekávali jsme 2." \
                % numdetected


def textresult_GPIO(p_result):
    if p_result[0] == 0:
        return u"Test GPIO proběhl úspěšně."
    else:
        return u"Při testování GPIO nastala chyba <div style=\"font-size: 11px;\">%s</div>" \
                % p_result[1]


TESTLIST = (
{
    "desc":
        u"test WAN portu",
    "testfunc": test_WAN,
    "interpretresult": textresult_WAN
},
{
    "desc":
        u"test LAN portu č. 1",
    "testfunc": test_LAN1,
    "interpretresult": textresult_LAN1
},
{
    "desc":
        u"test LAN portu č. 2",
    "testfunc": test_LAN_ping,
    "interpretresult": textresult_LAN2
},
{
    "desc":
        u"test LAN portu č. 3",
    "testfunc": test_LAN_ping,
    "interpretresult": textresult_LAN3
},
{
    "desc":
        u"test LAN portu č. 4",
    "testfunc": test_LAN_ping,
    "interpretresult": textresult_LAN4
},
{
    "desc":
        u"test LAN portu č. 5",
    "testfunc": test_LAN_ping,
    "interpretresult": textresult_LAN5
},
{
    "desc":
        u"test USB",
    "testfunc": test_USB,
    "interpretresult": textresult_USB
},
{
    "desc":
        u"test mini PCI express slotů",
    "testfunc": test_miniPCIe,
    "interpretresult": textresult_miniPCIe
},
{
    "desc":
        u"test GPIO",
    "testfunc": test_GPIO,
    "interpretresult": textresult_GPIO
},
)
