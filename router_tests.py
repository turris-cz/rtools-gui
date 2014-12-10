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


def test_serial_console(sc):
    characters = ['^', '!', '+', '@']
    batches = [
        (500, 4),
        (100, 4),
        (20, 4),
        (1, 4),
    ]

    # write part
    ch_index = 0
    output = ""
    for batch in batches:
        size, count = batch
        for i in range(count):
            # prepare line
            line = ""
            for k in range(size):
                line += characters[ch_index]
                ch_index = 0 if len(characters) - 1 <= ch_index else ch_index + 1
            output += sc.exec_("echo %s\n" % line, timeout=1, wait_interval=0.01)

    ch_needed = reduce(lambda y, x: x[0] * x[1] + y, batches, 0) / len(characters)

    errors = []
    # read part
    for ch in characters:
        ch_count = output.count(ch)
        if ch_needed > ch_count:
            errors.append("'%s' count (%d) &lt; %d" % (ch, ch_count, ch_needed))

    if errors:
        return (-1, "-1", ", ".join(errors), "Remote echo commands")
    else:
        return (0, "0", "Serial console seems to be working", "Remote echo commands")


def test_WAN(sc):
    time.sleep(2)  # wait for link

    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.100.2" % LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult

    cmdResult = runRemoteCmd(sc, "ifconfig %s 192.168.100.1" % TURRIS_WAN_IFACE)
    if cmdResult[0] != 0:
        return cmdResult

    time.sleep(1)  # wait for addresses to be set

    return runLocalCmd("ping -c 3 192.168.100.1")


def test_LAN(sc):
    cmdResult = runLocalCmd("sudo ifconfig %s 192.168.1.2" % LOCAL_TEST_IFACE)
    if cmdResult[0] != 0:
        return cmdResult

    time.sleep(3)  # wait for the addresses to be set

    return runLocalCmd("ping -c 3 192.168.1.1")


def test_USB(sc):
    cmd = "ls /dev/sd? 2> /dev/null | wc -l"
    cmdOut = sc.exec_(cmd)
    countSD = cmdOut.strip()
    if countSD.isdigit():
        countSD = int(countSD)
        if countSD == 3:
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
    # GPIO_OUT="224 225 226 227"
    # GPIO_IN="228 229 230 239"
    GPIO_OUT="224 225 227"
    GPIO_IN="228 229 239"
    for i in $GPIO_OUT; do echo out > /sys/class/gpio/gpio$i/direction; done
    for i in $GPIO_IN; do echo in > /sys/class/gpio/gpio$i/direction; done

    # for i in `seq 1 4`; do
    for i in `seq 1 3`; do
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
    # for i in `seq 1 4`; do
    for i in `seq 1 3`; do
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

    # GPIO_IN="224 225 226 227"
    # GPIO_OUT="228 229 230 239"
    GPIO_IN="224 225 227"
    GPIO_OUT="228 229 239"
    for i in $GPIO_OUT; do echo out > /sys/class/gpio/gpio$i/direction; done
    for i in $GPIO_IN; do echo in > /sys/class/gpio/gpio$i/direction; done

    # for i in `seq 1 4`; do
    for i in `seq 1 3`; do
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
    # for i in `seq 1 4`; do
    for i in `seq 1 3`; do
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


def test_SPI(sc):
    cmd = "spidev_test -D /dev/spidev0.0 | tail -n 1"
    cmdOut = sc.exec_(cmd)
    string = cmdOut.strip()
    status = sc.lastStatus()
    if status == '0':
        if string == "BA AD":
            return (0, "0", cmdOut, "Remote cmd:\n" + cmd)
        else:
            return (1, "1", cmdOut, "Remote cmd:\n" + cmd)
    else:
        return (-1, status, cmdOut, "Remote cmd:\n" + cmd)


def test_I2C(sc):
    return runRemoteCmd(sc, "i2cget -f -y 1 0x4c")


def textresult_generic(p_result):
    return "%s<br>returned:<br>%s<br>return code: %s" % (p_result[3], p_result[2], p_result[1])


def textresult_USB(p_result):
    if p_result[0] == -1:
        return textresult_generic(p_result)
    else:
        return u"Detekovali jsme jenom %s USB zařízení. Očekávali jsme 3." \
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
        "desc": u"test sériové konzole",
        "instructions": u"Připojte kabel č. 5 do konektoru J1.",
        "testfunc": test_serial_console,
        "interpretfailure": textresult_generic,
        "interactive": False,
    },
    {
        "desc": u"test WAN portu",
        "instructions": u"Zapojte testovací ethernet kabel do portu WAN.",
        "testfunc": test_WAN,
        "interpretfailure": textresult_generic,
        "interactive": True,
    },
    {
        "desc": u"test LAN portu č. 1",
        "instructions": u"Zapojte testovací ethernet kabel do portu LAN 1.",
        "testfunc": test_LAN,
        "interpretfailure": textresult_generic,
        "interactive": True,
    },
    {
        "desc": u"test LAN portu č. 2",
        "instructions": u"Zapojte testovací ethernet kabel do portu LAN 2.",
        "testfunc": test_LAN,
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
)
