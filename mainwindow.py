# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.mainwindow import Ui_MainWindow

from custom_exceptions import DbError
from utils import serialNumberValidator, MAX_SERIAL_LEN

# Include settings
from application import workflow, tests, qApp

def _removeItemFromGridLayout(layout, row, column):
    item = layout.itemAtPosition(row, column)
    item and layout.removeItem(item)
    return item

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    WORK_STATE_FAILED = "F"
    WORK_STATE_UNKNOWN = "U"
    WORK_STATE_PASSED = "P"
    WORK_STATE_RUNNING = "R"
    WORK_STATES = (
        WORK_STATE_FAILED,
        WORK_STATE_UNKNOWN,
        WORK_STATE_PASSED,
        WORK_STATE_RUNNING,
    )

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)  # create gui
        self.barcodeLineEdit.setMaxLength(MAX_SERIAL_LEN)
        self.inRunningMode = False

        # set icons for back and forward buttons
        self.scanButton.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight)
        )
        self.scanButton.setIconSize(QtCore.QSize(20, 20))

        self.backButton.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ArrowLeft)
        )
        self.backButton.setIconSize(QtCore.QSize(20, 20))

        # load the workflow into gui
        workflow_len = len(workflow.WORKFLOW)
        for i in range(workflow_len):
            self.addStep(i, workflow.WORKFLOW[i].name)
        # add spacers
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stepsLayout.addItem(spacer, workflow_len, 0)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stepsLayout.addItem(spacer, workflow_len, 1)

        # load the tests into gui
        tests_len = len(tests.TESTS)
        for i in range(tests_len):
            self.addTest(i, tests.TESTS[i].name)
        # add spacers
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.testsLayout.addItem(spacer, tests_len, 0)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.testsLayout.addItem(spacer, tests_len, 1)

        # open db connection
        qApp.loggerMain.info("Opening db connection.")
        if not qApp.connection.open():
            qApp.loggerMain.error("Connecting to db fails.")
            QtWidgets.QMessageBox.critical(
                self, "Chyba databáze",
                "<p>Nepodařilo se připojit do databáze. Zavírám aplikaci...</p>"
            )
            raise DbError(qApp.connection.lastError().text())
        qApp.loggerMain.info("Connected to database.")

    def loadRouter(self, router):
        # Set title
        self.serialNumberLabel.setText("%s (%s)" % (router.id, router.idHex))

        # Update steps
        passed = router.performedSteps['passed']  # step passed at least once
        failed = router.performedSteps['failed'] - passed
        for i in range(len(workflow.WORKFLOW)):
            if workflow.WORKFLOW[i].name in passed:
                self.updateStep(i, MainWindow.WORK_STATE_PASSED)
            elif workflow.WORKFLOW[i].name in failed:
                self.updateStep(i, MainWindow.WORK_STATE_FAILED)
            else:
                self.updateStep(i, MainWindow.WORK_STATE_UNKNOWN)
        for i in range(len(tests.TESTS)):
            self.updateTest(i, MainWindow.WORK_STATE_UNKNOWN)

    def cleanErrorMessage(self):
        self.errorLabel.setText("")

    def _updateProgressBars(self, enabled, overallMax=None):
            self.currentProgressBar.setEnabled(enabled)
            self.overallProgressBar.setEnabled(enabled)
            if overallMax:
                self.overallProgressBar.setMaximum(overallMax)
                self.overallProgressBar.setValue(0)

    def _statusToWidget(self, parent, status):
        if status == MainWindow.WORK_STATE_UNKNOWN:
            widget = QtWidgets.QLabel(parent)
            widget.setPixmap(
                QtWidgets.QApplication.style().standardIcon(
                    QtWidgets.QStyle.SP_TitleBarContextHelpButton
                ).pixmap(20, 20)
            )
        elif status == MainWindow.WORK_STATE_PASSED:
            widget = QtWidgets.QLabel(parent)
            widget.setPixmap(
                QtWidgets.QApplication.style().standardIcon(
                    QtWidgets.QStyle.SP_DialogApplyButton
                ).pixmap(20, 20)
            )
        elif status == MainWindow.WORK_STATE_FAILED:
            widget = QtWidgets.QLabel(parent)
            widget.setPixmap(
                QtWidgets.QApplication.style().standardIcon(
                    QtWidgets.QStyle.SP_DialogCloseButton
                ).pixmap(20, 20)
            )
        elif status == MainWindow.WORK_STATE_RUNNING:
            widget = QtWidgets.QProgressBar(parent)
            widget.setMaximumWidth(50)
            widget.setMaximumHeight(20)
            widget.setMaximum(0)
            widget.setMinimum(0)
            widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return widget

    def _addElement(self, layout, i, text, status):
        textLabel = QtWidgets.QLabel(text, self)
        textLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        layout.addWidget(textLabel, i, 0)
        layout.addWidget(self._statusToWidget(layout.parentWidget(), status), i, 1)

    def _updateElement(self, layout, i, status):
        if i < layout.rowCount():
            item = _removeItemFromGridLayout(layout, i, 1)
            item.widget().deleteLater()
            layout.addWidget(self._statusToWidget(layout.parentWidget(), status), i, 1)
        else:
            raise IndexError

    def addStep(self, i, text):
        self._addElement(self.stepsLayout, i, text, MainWindow.WORK_STATE_UNKNOWN)

    def updateStep(self, i, status):
        self._updateElement(self.stepsLayout, i, status)

    def addTest(self, i, text):
        self._addElement(self.testsLayout, i, text, MainWindow.WORK_STATE_UNKNOWN)

    def updateTest(self, i, status):
        self._updateElement(self.testsLayout, i, status)

    def enterRunningMode(self):
        self.backButton.setEnabled(False)
        self.startTestsButton.setEnabled(False)
        self.startStepsButton.setEnabled(False)
        self.inRunningMode = True

    def exitRunningMode(self):
        self.backButton.setEnabled(True)
        self.startTestsButton.setEnabled(True)
        self.startStepsButton.setEnabled(True)
        self.inRunningMode = False

    @QtCore.pyqtSlot()
    def switchToBarcode(self):
        # clear the error message
        self.cleanErrorMessage()

        # clear the barcode input
        self.barcodeLineEdit.clear()

        # switch to barcode
        self.stackedWidget.setCurrentWidget(self.barcodePage)

        # TODO clean router structure

    @QtCore.pyqtSlot()
    def checkBarcodeAndLoadRouter(self):
        # clear the error message
        self.cleanErrorMessage()

        serialNumber = self.barcodeLineEdit.text()
        if serialNumberValidator(serialNumber):

            self.stackedWidget.setCurrentWidget(self.workPage)

            # Set the router for the whole application
            self.loadRouter(qApp.useRouter(serialNumber))

        else:
            self.errorLabel.setText(u"'%s' je neplatné!" % serialNumber)

    @QtCore.pyqtSlot()
    def runSteps(self):
        qApp.loggerMain.info("Starting to run steps.")
        runner = qApp.prepareStepRunner()

        if not runner:
            # Nothing to be performed
            return

        # connect signals
        runner.runProgress.connect(self.updateProgress)
        runner.runStarted.connect(self.stepStarted)
        runner.runFinished.connect(self.stepFinished)
        runner.runsFinished.connect(self.stepsFinished)

        # start runner
        if runner.performRuns():
            self._updateProgressBars(True, len(qApp.stepPlan))
            self.enterRunningMode()

    @QtCore.pyqtSlot(int)
    def updateProgress(self, value):
        self.currentProgressBar.setValue(self.currentProgressBar.value() + value)

    @QtCore.pyqtSlot(int)
    def stepStarted(self, planIndex):
        name = workflow.WORKFLOW[qApp.stepPlan[planIndex]].name
        qApp.loggerMain.info("Starting step '%s'" % name)
        self.currentProgressBar.setValue(0)
        self.updateStep(qApp.stepPlan[planIndex], MainWindow.WORK_STATE_RUNNING)

    @QtCore.pyqtSlot(int, bool)
    def stepFinished(self, planIndex, passed):
        name = workflow.WORKFLOW[qApp.stepPlan[planIndex]].name
        msg = "Step '%s' finished - %s" % (name, ("PASSED" if passed else "FAILED"))
        qApp.loggerMain.info(msg) if passed else qApp.loggerMain.error(msg)
        state = MainWindow.WORK_STATE_PASSED if passed else MainWindow.WORK_STATE_FAILED
        self.overallProgressBar.setValue(self.overallProgressBar.value() + 1)
        self.updateStep(qApp.stepPlan[planIndex], state)
        qApp.router.storeStep(workflow.WORKFLOW[qApp.stepPlan[planIndex]].name, passed)

    @QtCore.pyqtSlot(int, int)
    def stepsFinished(self, passedCount, totalCount):
        msg = "Steps finished (%d/%d succeeded)" % (passedCount, totalCount)
        qApp.loggerMain.info(msg)
        self._updateProgressBars(False)
        qApp.router.incStepAttempt()
        self.exitRunningMode()

    def closeEvent(self, event):

        if self.inRunningMode:
            if QtWidgets.QMessageBox.question(
                self, "Pracuji",
                "<p>Program nyní provádí kritickou činnost a nebylo by dobré ho ukončovat.</p>"
                "<p>Přejete si přesto program ukončit?",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
            ) != QtWidgets.QMessageBox.Ok:
                event.ignore()
                return
            else:
                qApp.loggerMain.warn("closign the application in the middle of a run")

        # close the database
        if qApp.connection.isOpen():
            qApp.loggerMain.info("Closing db connection.")
            qApp.connection.close()

        event.accept()

    @QtCore.pyqtSlot()
    def runTests(self):
        qApp.loggerMain.info("Starting to run tests.")
        runner = qApp.prepareTestRunner()

        if not runner:
            # Nothing to be performed
            return

        # connect signals
        runner.runProgress.connect(self.updateProgress)
        runner.runStarted.connect(self.testStarted)
        runner.runFinished.connect(self.testFinished)
        runner.runsFinished.connect(self.testsFinished)

        # start runner
        if runner.performRuns():
            self._updateProgressBars(True, len(qApp.testPlan))
            self.enterRunningMode()

    @QtCore.pyqtSlot(int)
    def testStarted(self, planIndex):
        name = tests.TESTS[qApp.testPlan[planIndex]].name
        qApp.loggerMain.info("Starting test '%s'" % name)
        self.currentProgressBar.setValue(0)
        self.updateTest(qApp.testPlan[planIndex], MainWindow.WORK_STATE_RUNNING)

    @QtCore.pyqtSlot(int, bool)
    def testFinished(self, planIndex, passed):
        name = tests.TESTS[qApp.testPlan[planIndex]].name
        msg = "Test '%s' finished - passed %s" % (name, ("PASSED" if passed else "FAILED"))
        qApp.loggerMain.info(msg) if passed else qApp.loggerMain.error(msg)
        state = MainWindow.WORK_STATE_PASSED if passed else MainWindow.WORK_STATE_FAILED
        self.overallProgressBar.setValue(self.overallProgressBar.value() + 1)
        self.updateTest(qApp.testPlan[planIndex], state)
        qApp.router.storeTest(tests.TESTS[qApp.testPlan[planIndex]].name, passed)

    @QtCore.pyqtSlot(int, int)
    def testsFinished(self, passedCount, totalCount):
        msg = "Tests finished (%d/%d succeeded)" % (passedCount, totalCount)
        qApp.loggerMain.info(msg)
        self._updateProgressBars(False)
        qApp.router.incTestAttempt()
        if passedCount == totalCount:
            qApp.router.setRunSuccessful()
        self.exitRunningMode()
