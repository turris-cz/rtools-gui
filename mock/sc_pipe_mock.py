#!/usr/bin/python

import sys
import optparse

from PyQt5.QtCore import (
    QCoreApplication, QObject, pyqtSlot, QIODevice, QTimer
)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtSerialPort import QSerialPort


PLAN = {
    'ls': {
        'output': ".",
        'timeout': 1000,
    },
    'echo "###$?###"': {
        'output': '###0###',
        'timeout': 2000,
    },
}

def generatePlanFunction(key, watcher):
    def perform():
        watcher.serialConsoleReady(PLAN[key]['output'] + '\n')

    return perform

class Watcher(QObject):

    def __init__(self, server, logFile, device):
        super(Watcher, self).__init__()
        self.logFile = logFile
        self.server = server
        self.device = device
        self.server.newConnection.connect(self.inputClientConnected)

    @pyqtSlot(str)
    def serialConsoleReady(self, data):
        self.logFile.write(data)
        self.logFile.flush()

        socket = QLocalSocket()
        socket.connectToServer("serial-output" + self.device.replace('/','-'))
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

        self.logFile.write(data)
        self.logFile.flush()

        data = data.strip()
        if data in PLAN:
            QTimer.singleShot(PLAN[data]['timeout'], generatePlanFunction(data, self))


if __name__ == '__main__':

    # Parse the command line options
    optparser = optparse.OptionParser(
        "usage: %prog"
        "--device <device> "
        "--baudrate <baudrate> "
        "--log-file <file> "
    )
    optparser.add_option("-d", "--device", dest='dev', type='string', help='device')
    optparser.add_option("-b", "--baudrate", dest='rate', type='int', help='baudrate')
    optparser.add_option("-l", "--log-file", dest='logFile', type='string', help='logfile')

    (options, args) = optparser.parse_args()
    options.dev or optparser.error("device not set")
    options.rate or optparser.error("baudrate not set")
    options.logFile or optparser.error("logfile not set")

    app = QCoreApplication(sys.argv)

    # init input server
    inputServer = QLocalServer()
    QLocalServer.removeServer("serial-input" + options.dev.replace('/','-'))
    inputServer.listen("serial-input" + options.dev.replace('/','-')) or sys.exit(1)

    # init stop server
    stopServer = QLocalServer()
    QLocalServer.removeServer("stop-server" + options.dev.replace('/','-'))
    stopServer.listen("stop-server" + options.dev.replace('/','-')) or sys.exit(1)
    stopServer.newConnection.connect(app.quit)

    with open(options.logFile, "a", 0) as logFile:
        logFile.write("THIS IS MOCK SCRIPT OUTPUT NOT ACTUAL SERIAL CONSOLE OUTPUT\n\n")
        watcher = Watcher(inputServer, logFile, options.dev)
        sys.exit(app.exec_())
