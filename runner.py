import os
import sys

from datetime import datetime
from PyQt5 import QtCore

from application import qApp, settings

class Runner(QtCore.QObject):
    TYPE_STEPS = 'steps'
    TYPE_TESTS = 'tests'

    startWorker = QtCore.pyqtSignal()
    runsFinished = QtCore.pyqtSignal(int, int)
    runStarted = QtCore.pyqtSignal(int)
    runFinished = QtCore.pyqtSignal(int, bool)
    runProgress = QtCore.pyqtSignal(int)

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

        logname = "%s-%08d-%s-%04d-%s.txt" % (
            self.routerId, self.runId, self.typeName, self.attempt,
            datetime.now().strftime("%Y-%m-%d-%H-%M")
        )
        self.logFile = os.path.join(settings.LOG_ROUTERS_DIR, logname)

    def performRuns(self):
        self.current = 0
        self.passedCount = 0
        self.result = True

        # prepare the console pipe process
        qApp.loggerMain.info("Starting serial console pipe process.")
        pipePath = os.path.join(sys.path[0], 'sc_pipe.py')
        self.pipeProcess = QtCore.QProcess()
        self.pipeProcess.start(
            pipePath, [
                '-b', str(settings.SERIAL_CONSOLE_SETTINGS['baudrate']),
                '-d', settings.SERIAL_CONSOLE_SETTINGS['device'],
                '-l', self.logFile,
            ]
        )

        if self.pipeProcess.waitForStarted(500):  # wait for 0.5s to start the process
            # start the runs
            self.runSingle(self.current)
            qApp.loggerMain.info("Serial console pipe process started.")
            self.running = True
            return True
        else:
            qApp.loggerMain.error("Failed to start serial console pipe process. Run terminated!")
            return False

    def finish(self):
        self.runsFinished.emit(self.passedCount, len(self.runlist))
        # Force kill the process
        self.pipeProcess.kill()
        qApp.loggerMain.info("Terminating serial console pipe process.")
        self.running = False

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

    def runSingle(self, i):

        self.worker = self.runlist[i].getWorker(self.logFile)
        self.thread = QtCore.QThread(self)
        self.worker.finished.connect(self.runDone)
        self.worker.progress.connect(self.workerProgress)
        self.startWorker.connect(self.worker.start)
        self.worker.moveToThread(self.thread)
        # Start the thread event loop
        self.thread.start()
        # Run the worker
        self.startWorker.emit()
        # Notify others
        self.runStarted.emit(i)

        # TODO start timer and kill the thread if needed
