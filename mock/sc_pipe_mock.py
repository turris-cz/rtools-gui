#!/usr/bin/env python2

import optparse
import prctl
import signal
import sys
import time

from PyQt5.QtCore import (
    QCoreApplication, QObject, pyqtSlot, QTimer
)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

from utils import PrefixFile


def generatePlanFunction(watcher, output):
    def perform():
        watcher.serialConsoleReady(output)
    return perform


class Watcher(QObject):

    def __init__(self, server, logFile, device, plan):
        super(Watcher, self).__init__()
        self.logFile = logFile
        self.server = server
        self.device = device
        self.server.newConnection.connect(self.inputClientConnected)
        self.plan = plan

    @pyqtSlot(str)
    def serialConsoleReady(self, data):
        file_data = data[:-1] if data[-1] == '\n' else data
        self.logFile.write(file_data)
        self.logFile.flush()

        socket = QLocalSocket()
        socket.connectToServer("serial-output" + self.device.replace('/', '-'))
        socket.write(data)
        socket.flush()
        socket.disconnectFromServer()

    @pyqtSlot()
    def inputClientConnected(self):
        clientConnection = self.server.nextPendingConnection()

        # Connect read ready
        clientConnection.readyRead.connect(self.inputClientReadReady)

        # Connect socket disconnected
        clientConnection.disconnected.connect(self.inputClientDisconnected)

    @pyqtSlot()
    def inputClientDisconnected(self):
        clientConnection = self.sender()
        clientConnection.flush()
        clientConnection.disconnectFromServer()

    @pyqtSlot()
    def inputClientReadReady(self):
        data = str(self.sender().readAll())
        data = "\n%s" % data

        self.logFile.write(data)
        self.logFile.flush()

        data = data.strip()
        if data in self.plan:
            for timeout, output in self.plan[data]:
                QTimer.singleShot(timeout, generatePlanFunction(self, output + '\n'))


def runMain(plan):

    # kill process when parent dies
    prctl.set_pdeathsig(signal.SIGTERM)

    # Parse the command line options
    optparser = optparse.OptionParser(
        "usage: %prog"
        "--device <device> "
        "--baudrate <baudrate> "
        "--log-file <file> "
        "--prefix <prefix> "
        "--start-time <float> "
    )
    optparser.add_option("-d", "--device", dest='dev', type='string', help='device')
    optparser.add_option("-b", "--baudrate", dest='rate', type='int', help='baudrate')
    optparser.add_option("-l", "--log-file", dest='logFile', type='string', help='logfile')
    optparser.add_option("-p", "--prefix", dest='prefix', type='string', help='prefix')
    optparser.add_option(
        "-s", "--start-time", dest='startTime', type='float', help='startTime',
        default=time.time()
    )

    (options, args) = optparser.parse_args()
    options.dev or optparser.error("device not set")
    options.rate or optparser.error("baudrate not set")
    options.logFile or optparser.error("logfile not set")
    prefix = options.prefix or ""

    app = QCoreApplication(sys.argv)

    # init input server
    inputServer = QLocalServer()
    QLocalServer.removeServer("serial-input" + options.dev.replace('/', '-'))
    inputServer.listen("serial-input" + options.dev.replace('/', '-')) or sys.exit(1)

    # init stop server
    stopServer = QLocalServer()
    QLocalServer.removeServer("stop-server" + options.dev.replace('/', '-'))
    stopServer.listen("stop-server" + options.dev.replace('/', '-')) or sys.exit(1)
    stopServer.newConnection.connect(app.quit)

    with PrefixFile(options.logFile, "a", 0, prefix=prefix, startTime=options.startTime) as logFile:
        initial_msg = "\nTHIS IS MOCK SCRIPT OUTPUT NOT ACTUAL SERIAL CONSOLE OUTPUT\n\n"
        logFile.write(initial_msg)
        logFile.flush()
        watcher = Watcher(inputServer, logFile, options.dev, plan)
        sys.exit(app.exec_())
