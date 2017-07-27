#!/usr/bin/python

import optparse
import prctl
import signal
import sys

from PyQt5.QtCore import (
    QCoreApplication, QSocketNotifier, QObject, pyqtSlot
)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket


class Watcher(QObject):

    def __init__(self, server, device):
        super(Watcher, self).__init__()
        self.server = server
        self.device = device
        self.server.newConnection.connect(self.outputClientConnected)

    @pyqtSlot(int)
    def stdinRead(self, socket):
        data = sys.stdin.readline()

        socket = QLocalSocket()
        socket.connectToServer("serial-input" + self.device.replace('/', '-'))
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

    # kill process when parent dies
    prctl.set_pdeathsig(signal.SIGTERM)

    # Parse the command line options
    optparser = optparse.OptionParser(
        "usage: %prog"
        "--device <device>"
    )
    optparser.add_option("-d", "--device", dest='dev', type='string', help='device')

    (options, args) = optparser.parse_args()
    options.dev or optparser.error("device not set")

    app = QCoreApplication(sys.argv)

    # load stdin notifier
    notifier = QSocketNotifier(sys.stdin.fileno(), QSocketNotifier.Read)

    # init output server
    outputServer = QLocalServer()
    QLocalServer.removeServer("serial-output" + options.dev.replace('/', '-'))
    outputServer.listen("serial-output" + options.dev.replace('/', '-')) or sys.exit(1)

    watcher = Watcher(outputServer, options.dev)
    notifier.activated.connect(watcher.stdinRead)

    sys.exit(app.exec_())
