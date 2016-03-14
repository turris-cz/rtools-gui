from PyQt5 import QtCore

class Runner(QtCore.QObject):
    startWorker = QtCore.pyqtSignal()
    runsFinished = QtCore.pyqtSignal(bool)
    runStarted = QtCore.pyqtSignal(int)
    runFinished = QtCore.pyqtSignal(int, bool)
    runProgress = QtCore.pyqtSignal(int)

    def __init__(self, runlist):
        super(Runner, self).__init__()
        # TODO log run list
        print "RUNLIST", runlist
        self.runlist = runlist
        self.current = 0
        self.result = True

    def performRuns(self):
        self.current = 0
        self.result = True
        self.runSingle(self.current)

    @QtCore.pyqtSlot(bool)
    def runDone(self, result):
        # stop the thread
        self.thread.quit()

        if not result and not self.runlist[self.current].continueOnFailure:
            self.runFinished.emit(self.current, False)
            self.runsFinished.emit(False)
            return

        self.runFinished.emit(self.current, result)
        self.result = self.result and result

        self.current += 1
        if self.current < len(self.runlist):
            # Moving to next item
            self.runSingle(self.current)
        else:
            # All finished
            self.runsFinished.emit(self.result)

    @QtCore.pyqtSlot(int)
    def workerProgress(self, value):
        return self.runProgress.emit(value)

    def runSingle(self, i):

        self.worker = self.runlist[i].getWorker()
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
