#!/usr/bin/python

import sys
import optparse

from PyQt5.QtCore import (
    QCoreApplication, QObject, pyqtSlot, QIODevice
)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtSerialPort import QSerialPort


class Watcher(QObject):

    def __init__(self, sc, server, logFile):
        super(Watcher, self).__init__()
        self.logFile = logFile
        self.sc = sc
        self.sc.readyRead.connect(self.serialConsoleReady)
        self.server = server
        self.server.newConnection.connect(self.inputClientConnected)

    @pyqtSlot()
    def serialConsoleReady(self):
        data = self.sc.readAll()
        self.logFile.write(data)
        self.logFile.flush()

        socket = QLocalSocket()
        socket.connectToServer("serial-output")
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
        data = self.sender().readAll()
        self.sc.writeData(data)


if __name__ == '__main__':

    # Parse the command line options
    optparser = optparse.OptionParser(
        "usage: %prog --device <device> --baudrate <baudrate> --log-file <file>\n"
    )
    optparser.add_option("-d", "--device", dest='dev', type='string', help='device')
    optparser.add_option("-b", "--baudrate", dest='rate', type='int', help='baudrate')
    optparser.add_option("-l", "--log-file", dest='logFile', type='string', help='logfile')

    (options, args) = optparser.parse_args()
    options.dev or optparser.error("device not set")
    options.rate or optparser.error("baudrate not set")
    options.logFile or optparser.error("logfile not set")

    app = QCoreApplication(sys.argv)

    # init serial console
    sc = QSerialPort(options.dev)
    sc.setBaudRate(options.rate)
    sc.open(QIODevice.ReadWrite) or sys.exit(1)

    # init input server
    inputServer = QLocalServer()
    QLocalServer.removeServer("serial-input")
    inputServer.listen("serial-input") or sys.exit(1)

    with open(options.logFile, "a") as logFile:
        watcher = Watcher(sc, inputServer, logFile)
        sys.exit(app.exec_())
