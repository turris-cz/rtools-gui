import os
import sys
import time

from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtNetwork import QLocalSocket

from application import qApp, settings
from utils import backupFile, backupAppLog


class Runner(QtCore.QObject):
    TYPE_STEPS = 'steps'
    TYPE_TESTS = 'tests'

    startWorker = QtCore.pyqtSignal()
    runsFinished = QtCore.pyqtSignal(int, int)
    runStarted = QtCore.pyqtSignal(int)
    runFinished = QtCore.pyqtSignal(int, bool)
    runProgress = QtCore.pyqtSignal(int)
    printInstructions = QtCore.pyqtSignal(str)

    def __init__(self, routerId, runlist, runId, typeName, attempt):
        super(Runner, self).__init__()
        qApp.loggerMain.info("Runlist: %s" % ", ".join([e.name for e in runlist]))

        # set the variables
        self.routerId = routerId
        self.runlist = runlist
        self.runId = runId
        self.typeName = typeName
        self.attempt = attempt
        self.running = False
        self.pipeProcesses = []
        self.startTime = time.time()

        logname = "%s-%08d-%s-%04d-%s.txt" % (
            self.routerId, self.runId, self.typeName, self.attempt,
            datetime.now().strftime("%Y-%m-%d-%H-%M")
        )
        self.logFile = os.path.join(settings.LOG_ROUTERS_DIR, logname)

    def _quitRunningScPipe(self, name):
        # sc_pipe should listen on this socket and when a client connects it should quit
        socket = QLocalSocket()
        socket.connectToServer(name)
        socket.disconnectFromServer()

    def _startPipeProcess(self, scName, logFile):
        scSettings = settings.SERIAL_CONSOLE[scName]

        # prepare the console pipe process
        self._quitRunningScPipe("stop-server" + scSettings['device'].replace('/', '-'))
        mock = scSettings.get('mock', None)
        if mock:
            pipePath = mock
        else:
            pipePath = os.path.join(sys.path[0], 'sc_pipe.py')
        pipeProcess = QtCore.QProcess()
        pipeProcess.start(
            pipePath, [
                '-b', str(scSettings['baudrate']),
                '-d', scSettings['device'],
                '-l', logFile,
                '-p', scName,
                '-s', str(self.startTime),
            ]
        )
        qApp.loggerMain.info(
            "Starting %s serial console pipe process. (%s %s)" %
            (scName, pipePath, " ".join(pipeProcess.arguments()))
        )

        if pipeProcess.waitForStarted(500):  # wait for 0.5s to start the process
            qApp.loggerMain.info(
                "The %s serial console pipe process started. (PID=%d)"
                % (scName, pipeProcess.pid())
            )
            self.pipeProcesses.append(pipeProcess)
            return True
        else:
            qApp.loggerMain.error(
                "Failed to start %s serial console pipe process. Run terminated!" % scName)
            return False

    def performRuns(self):
        self.current = 0
        self.passedCount = 0
        self.result = True
        self.pipeProcesses = []

        # prepare the console pipe processes
        if self._startPipeProcess("router", self.logFile) \
                and self._startPipeProcess("tester", self.logFile):
            # wait a second before starting the process
            QtCore.QThread.sleep(1)
            # start the runs
            self.runSingle(self.current)
            self.running = True
            return True
        else:
            return False

    def finish(self):
        self.runsFinished.emit(self.passedCount, len(self.runlist))
        qApp.loggerMain.info("Terminating serial console pipe processes.")
        # Force kill the processes
        [e.kill() for e in self.pipeProcesses]
        self.running = False
        backupFile(self.logFile)
        backupAppLog()

    @QtCore.pyqtSlot(bool)
    def runDone(self, result):
        # stop the thread
        self.thread.quit()

        if result:
            self.passedCount += 1

        if not result and not self.runlist[self.current].continueOnFailure:
            self.runFinished.emit(self.current, False)
            self.finish()
            return

        self.runFinished.emit(self.current, result)
        self.result = self.result and result

        self.current += 1
        if self.current < len(self.runlist):
            # Moving to next item
            self.runSingle(self.current)
        else:
            # All finished
            self.finish()

    @QtCore.pyqtSlot(int)
    def workerProgress(self, value):
        return self.runProgress.emit(value)

    @QtCore.pyqtSlot(str)
    def firwareObtained(self, firmware):
        qApp.loggerMain.info("Firmware obtained - %s" % firmware)
        qApp.router.storeFirmware(firmware)

    @QtCore.pyqtSlot(int, str)
    def ramObtained(self, ram, phase):
        qApp.loggerMain.info("Ram obtained - %d" % ram)
        qApp.router.storeRam(ram, phase)

    @QtCore.pyqtSlot(str, str)
    def eepromObtained(self, eeprom, phase):
        qApp.loggerMain.info("Eeprom obtained - %s" % eeprom)
        qApp.router.storeEeprom(eeprom, phase)

    @QtCore.pyqtSlot(str, str)
    def mcuObtained(self, bootloader, image):
        qApp.loggerMain.info("MCU bootloader obtained - %s" % bootloader)
        qApp.loggerMain.info("MCU image obtained - %s" % image)
        qApp.router.storeMcu(bootloader, image)

    @QtCore.pyqtSlot(str)
    def ubootObtained(self, image):
        qApp.loggerMain.info("Uboot image obtained - %s" % image)
        qApp.router.storeUboot(image)

    def runSingle(self, i):

        # Print instructions if needed
        if hasattr(self.runlist[i], "instructions"):
            self.printInstructions.emit(self.runlist[i].instructions)

        self.worker = self.runlist[i].getWorker(self.logFile, self.startTime)
        self.thread = QtCore.QThread(self)
        self.worker.finished.connect(self.runDone)
        self.worker.progress.connect(self.workerProgress)
        self.worker.firmware.connect(self.firwareObtained)
        self.worker.ram.connect(self.ramObtained)
        self.worker.eeprom.connect(self.eepromObtained)
        self.worker.mcu.connect(self.mcuObtained)
        self.worker.uboot.connect(self.ubootObtained)
        self.startWorker.connect(self.worker.start)
        self.worker.moveToThread(self.thread)
        # Start the thread event loop
        self.thread.start()
        # Run the worker
        self.startWorker.emit()
        # Notify others
        self.runStarted.emit(i)

        # TODO start timer and kill the thread if needed
