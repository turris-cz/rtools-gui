#!/usr/bin/python

import sys
import optparse

from PyQt5.QtCore import (
    QCoreApplication, QSocketNotifier, QObject, pyqtSlot, QIODevice,
)
from PyQt5.QtSerialPort import QSerialPort


class StdinWatch(QObject):

    def __init__(self, sc):
        super(StdinWatch, self).__init__()
        self.sc = sc

    @pyqtSlot(int)
    def stdinRead(self, socket):
        data = sys.stdin.readline()
        self.sc.writeData(data)

    @pyqtSlot()
    def serialConsoleReady(self):
        data = self.sc.readAll()
        sys.stdout.write(str(data))


if __name__ == '__main__':

    # Parse the command line options
    optparser = optparse.OptionParser(
        "usage: %prog --device <device> --baudrate <baudrate>\n"
    )
    optparser.add_option("-d", "--device", dest='dev', type='string', help='device')
    optparser.add_option("-b", "--baudrate", dest='rate', type='int', help='baudrate')

    (options, args) = optparser.parse_args()
    options.dev or optparser.error("device not set")
    options.rate or optparser.error("baudrate not set")

    app = QCoreApplication(sys.argv)

    # init serial console
    sc = QSerialPort(options.dev)
    sc.setBaudRate(options.rate)
    sc.open(QIODevice.ReadWrite) or sys.exit(1)

    notifier = QSocketNotifier(sys.stdin.fileno(), QSocketNotifier.Read)
    watch = StdinWatch(sc)
    notifier.activated.connect(watch.stdinRead)
    sc.readyRead.connect(watch.serialConsoleReady)

    sys.exit(app.exec_())
