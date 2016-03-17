#!/usr/bin/python

import sys

from PyQt5.QtCore import (
    QCoreApplication, QSocketNotifier, QObject, pyqtSlot
)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket


class Watcher(QObject):

    def __init__(self, server):
        super(Watcher, self).__init__()
        self.server = server
        self.server.newConnection.connect(self.outputClientConnected)

    @pyqtSlot(int)
    def stdinRead(self, socket):
        data = sys.stdin.readline()

        socket = QLocalSocket()
        socket.connectToServer("serial-input")
        socket.write(data)
        socket.flush()
        socket.disconnectFromServer()

    @pyqtSlot()
    def outputClientConnected(self):
        clientConnection = self.server.nextPendingConnection()

        # Connect read ready
        clientConnection.readyRead.connect(self.outputClientReadReady)

        # Connect socket disconnected
        clientConnection.disconnected.connect(self.outputClientDisconnected)

    @pyqtSlot()
    def outputClientDisconnected(self):
        clientConnection = self.sender()
        clientConnection.flush()
        clientConnection.disconnectFromServer()

    @pyqtSlot()
    def outputClientReadReady(self):
        data = self.sender().readAll()
        sys.stdout.write(data)


if __name__ == '__main__':

    app = QCoreApplication(sys.argv)

    # load stdin notifier
    notifier = QSocketNotifier(sys.stdin.fileno(), QSocketNotifier.Read)

    # init output server
    outputServer = QLocalServer()
    QLocalServer.removeServer("serial-output")
    outputServer.listen("serial-output") or sys.exit(1)

    watcher = Watcher(outputServer)
    notifier.activated.connect(watcher.stdinRead)

    sys.exit(app.exec_())
