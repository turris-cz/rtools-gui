# coding=utf-8

# this file defines tests which are run after successful flashing
# it is a tuple of tests, each of which contains description for
# a person executing the tests and second is a function which takes
# SerialConsole object and executest the tests
# a test can yield -1 - unparsable command output
#                  >=0 - result of the test


import subprocess
import time
from shlex import split
from settings import LOCAL_TEST_IFACE, TURRIS_WAN_IFACE


# results from
#     runLocalCmd
#     runRemoteCmd
#     test_*
#     are in the form
#     (
#         int exit_status (-1 if not a number),
#         str exit_status,
#         str command_output,
#         str ("Local cmd:\n" | "Remote cmd\n:" + command)
#    )


def runLocalCmd(cmdstr):
    p = subprocess.Popen(split(cmdstr), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    retCode = p.wait()
    stdOut = p.stdout.read()
    return (retCode, str(retCode), stdOut, "Local cmd:\n" + cmdstr)


def runRemoteCmd(sc, cmdstr):
    stdOut = sc.exec_(cmdstr)
    cmdStatus = sc.lastStatus()
    intCmdStatus = int(cmdStatus) if cmdStatus.isdigit() else -1
    return (intCmdStatus, cmdStatus, stdOut, "Remote cmd:\n" + cmdstr)


def test_WAN(sc):
    time.sleep(2) # wait for link
    
    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.100.2" % LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult
    
    cmdResult = runRemoteCmd(sc, "ifconfig %s 192.168.100.1" % TURRIS_WAN_IFACE)
    if cmdResult[0] != 0:
        return cmdResult
    
    time.sleep(1) # wait for addresses to be set
    
    return runLocalCmd("ping -c 3 192.168.100.1")


def test_LAN1(sc):
    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.1.2" % LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult
    
    time.sleep(1) # wait for the addresses to be set
    
    return test_LAN_ping(sc)


def test_LAN_ping(sc):
    time.sleep(2) # wait for link
    return runLocalCmd("ping -c 3 192.168.1.1")


def test_USB(sc):
    cmd = "ls /dev/sd? 2> /dev/null | wc -l"
    cmdOut = sc.exec_(cmd)
    countSD = cmdOut.strip()
    if countSD.isdigit():
        countSD = int(countSD)
        if countSD == 2:
            return (0, "0", cmdOut, "Remote cmd:\n" + cmd)
        else:
            return (1, "1", cmdOut, "Remote cmd:\n" + cmd)
    else:
        return (-1, sc.lastStatus(), cmdOut, "Remote cmd:\n" + cmd)


def test_miniPCIe(sc):
    cmd = "cat /sys/bus/pci/devices/*/vendor | grep -c '0x168c'"
    cmdOut = sc.exec_(cmd)
    countPci = cmdOut.strip()
    if countPci.isdigit():
        countPci = int(countPci)
        if countPci == 2:
            return (0, "0", cmdOut, "Remote cmd:\n" + cmd)
        else:
            return (1, "1", cmdOut, "Remote cmd:\n" + cmd)
    else:
        return (-1, sc.lastStatus(), cmdOut, "Remote cmd:\n" + cmd)


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

    for i in `seq 1 4`; do
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
    for i in `seq 1 4`; do
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
    cmdOut = sc.exec_(funcdef)
    if not cmdOut:
        return runRemoteCmd(sc, "( set -e; for i in `seq 10`; do gpiotest; done; )")
    else:
        return (-1, sc.lastStatus(), cmdOut, "Remote cmd:\n<long gpiotest function definition>")

def textresult_generic(p_result):
    return  "%s<br>returned:<br>%s<br>return code: %s" % (p_result[3], p_result[2], p_result[1])


def textresult_LAN1(p_result):
    return p_result[1]


def textresult_LAN2(p_result):
    return p_result[1]


def textresult_LAN3(p_result):
    return p_result[2]


def textresult_LAN4(p_result):
    return p_result[1]


def textresult_LAN5(p_result):
    return p_result[1]


def textresult_USB(p_result):
    if p_result[0] == -1:
        return textresult_generic(p_result)
    else:
        return u"Detekovali jsme jenom %s USB zařízení. Očekávali jsme 2." \
                % p_result[2].strip()


def textresult_miniPCIe(p_result):
    if p_result[0] == -1:
        return textresult_generic(p_result)
    else:
        num_slots = p_result[2].strip()
        if num_slots == "0":
            return u"Nedetekovali jsme žádný PCI express slot. Očekávali jsme 2."
        elif num_slots == "1":
            return u"Detekovali jsme jenom 1 PCI express slot. Očekávali jsme 2."
        else:
            return u"Detekovali jsme jenom %s PCI express sloty. Očekávali jsme 2." % num_slots


TESTLIST = (
{
    "desc": u"test WAN portu",
    "instructions": u"Zapojte testovací ethernet kabel do portu WAN.",    
    "testfunc": test_WAN,
    "interpretfailure": textresult_generic
},
{
    "desc": u"test LAN portu č. 1",
    "instructions": u"Zapojte testovací ethernet kabel do portu LAN 1.",
    "testfunc": test_LAN1,
    "interpretfailure": textresult_generic
},
{
    "desc": u"test LAN portu č. 2",
    "instructions": u"Zapojte testovací ethernet kabel do portu LAN 2.",
    "testfunc": test_LAN_ping,
    "interpretfailure": textresult_generic
},
{
    "desc": u"test LAN portu č. 3",
    "instructions": u"Zapojte testovací ethernet kabel do portu LAN 3.",
    "testfunc": test_LAN_ping,
    "interpretfailure": textresult_generic
},
{
    "desc": u"test LAN portu č. 4",
    "instructions": u"Zapojte testovací ethernet kabel do portu LAN 4.",
    "testfunc": test_LAN_ping,
    "interpretfailure": textresult_generic
},
{
    "desc": u"test LAN portu č. 5",
    "instructions": u"Zapojte testovací ethernet kabel do portu LAN 5.",
    "testfunc": test_LAN_ping,
    "interpretfailure": textresult_generic
},
{
    "desc": u"test USB",
    "instructions": u"Zkontrolujte připojení USB klíčů.",
    "testfunc": test_USB,
    "interpretfailure": textresult_USB
},
{
    "desc": u"test mini PCI express slotů",
    "instructions": u"Zkontrolujte připojení mini PCIe karet.",
    "testfunc": test_miniPCIe,
    "interpretfailure": textresult_miniPCIe
},
{
    "desc": u"test GPIO",
    "instructions": u"Zkontrolujte připojení GPIO přípravku.",
    "testfunc": test_GPIO,
    "interpretfailure": textresult_generic
},
)
