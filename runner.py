import os

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
        self.routerId = routerId
        self.runlist = runlist
        self.runId = runId
        self.typeName = typeName
        self.attempt = attempt
        self.current = 0
        self.passedCount = 0
        self.result = True

    def performRuns(self):
        self.current = 0
        self.result = True
        self.runSingle(self.current)

    @QtCore.pyqtSlot(bool)
    def runDone(self, result):
        # stop the thread
        self.thread.quit()

        if result:
            self.passedCount += 1

        if not result and not self.runlist[self.current].continueOnFailure:
            self.runFinished.emit(self.current, False)
            self.runsFinished.emit(self.passedCount, len(self.runlist))
            return

        self.runFinished.emit(self.current, result)
        self.result = self.result and result

        self.current += 1
        if self.current < len(self.runlist):
            # Moving to next item
            self.runSingle(self.current)
        else:
            # All finished
            self.runsFinished.emit(self.passedCount, len(self.runlist))

    @QtCore.pyqtSlot(int)
    def workerProgress(self, value):
        return self.runProgress.emit(value)

    def runSingle(self, i):

        filename = "%s-%08d-%s-%04d-%s.txt" % (
            self.routerId, self.runId, self.typeName, self.attempt,
            datetime.now().strftime("%Y-%m-%d-%H-%M")
        )
        dirname = settings.LOG_ROUTERS_DIR

        self.worker = self.runlist[i].getWorker(os.path.join(dirname, filename))
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
