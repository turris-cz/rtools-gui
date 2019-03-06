# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.mainwindow import Ui_MainWindow

from custom_exceptions import DbError, IncorrectSerialNumber
from utils import MAX_SERIAL_LEN, backupAppLog

from application import qApp, settings

if qApp.run_offline:
    from mock.db_wrapper import restoreRecovery, getLastRunsResults
else:
    from db_wrapper import restoreRecovery, getLastRunsResults


def _removeItemFromGridLayout(layout, row, column):
    item = layout.itemAtPosition(row, column)
    if item:
        layout.removeItem(item)
        item.widget().hide()
        item.widget().deleteLater()


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

        # don't open db connection if started in isolated environment
        if not qApp.run_offline:
            qApp.loggerMain.info("Opening db connection.")
            if not qApp.connection.open():
                qApp.loggerMain.error("Connecting to db fails.")
                QtWidgets.QMessageBox.critical(
                    self, "Chyba databáze",
                    """<p>Nepodařilo se připojit do databáze. Zavírám aplikaci...</p>
                    <p>Pro spuštění bez databáze spusťte program s konfigurací pro offline režim.</p>
                    <p>RTOOLS_SETTINGS='settings.omnia_offline' ./rtools-gui.py</p>
                    """
                )
                raise DbError(qApp.connection.lastError().text())
            qApp.loggerMain.info("Connected to database.")

        # perform queries which weren't performed last time
        restoreRecovery()

        # read last runs
        self.drawLastAttempts(getLastRunsResults())

        # tests/steps only
        if qApp.tests_only:
            qApp.loggerMain.info("Tests only option used.")
            self.stepFrame.setVisible(False)
            self.stepsStartWidget.setVisible(False)
            self.titleLabel.setText("Testování")
        if qApp.steps_only:
            qApp.loggerMain.info("Steps only option used.")
            self.testFrame.setVisible(False)
            self.testsStartWidget.setVisible(False)
            self.titleLabel.setText("Oživování")

        # set the custom titles
        if settings.CUSTOM_INIT_TITLE:
            self.titleLabel.setText(settings.CUSTOM_INIT_TITLE)

        # set upper labels
        self.regionLabel.setText(settings.REGION)
        self.ramLabel.setText("%dG" % settings.ROUTER_RAMSIZE)
        self.modeLabel.setText("%s" % settings.MODE_NAME)

        # set workstation label
        self.workstationTestLabel.setHidden(True)

        # blink timer
        self.blinkSwitch = True
        self.blinkTimer = QtCore.QTimer()
        self.blinkTimer.timeout.connect(self.blinkTitle)

    def loadWorkflows(self):
        # clear the layouts first
        item = self.stepsLayout.takeAt(0)
        while item:
            widget = item.widget()
            if widget:
                widget.setParent(None)
            item = self.stepsLayout.takeAt(0)

        item = self.testsLayout.takeAt(0)
        while item:
            widget = item.widget()
            if widget:
                widget.setParent(None)
            item = self.testsLayout.takeAt(0)

        # load the workflow into gui
        workflow_len = len(qApp.workflow.WORKFLOW)
        for i in range(workflow_len):
            self.addStep(i, qApp.workflow.WORKFLOW[i].name)
        # add spacers
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stepsLayout.addItem(spacer, workflow_len, 0)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stepsLayout.addItem(spacer, workflow_len, 1)
        spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.stepsLayout.addItem(spacer, workflow_len + 1, 0)

        # load the tests into gui
        tests_len = len(qApp.tests.TESTS)
        for i in range(tests_len):
            self.addTest(i, qApp.tests.TESTS[i].name)
        # add spacers
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.testsLayout.addItem(spacer, tests_len, 0)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.testsLayout.addItem(spacer, tests_len, 1)
        spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.testsLayout.addItem(spacer, tests_len + 1, 0)

    def loadRouter(self, router):
        # Set title
        self.setTitle()

        # Load the workflow
        self.loadWorkflows()

        # Update steps
        passed = router.performedSteps['passed']  # step passed at least once
        failed = router.performedSteps['failed'] - passed
        for i in range(len(qApp.workflow.WORKFLOW)):
            if qApp.workflow.WORKFLOW[i].name in passed:
                self.updateStep(i, MainWindow.WORK_STATE_PASSED)
            elif qApp.workflow.WORKFLOW[i].name in failed:
                self.updateStep(i, MainWindow.WORK_STATE_FAILED)
            else:
                self.updateStep(i, MainWindow.WORK_STATE_UNKNOWN)
        for i in range(len(qApp.tests.TESTS)):
            self.updateTest(i, MainWindow.WORK_STATE_UNKNOWN)

        # update buttons
        self.startTestsButton.setEnabled(qApp.router.canStartTests)
        self.startStepsButton.setEnabled(qApp.router.canStartSteps)

        # focus to buttons
        if self.startTestsButton.isEnabled() and self.startTestsButton.isVisible():
            self.startTestsButton.setFocus()
        if self.startStepsButton.isEnabled() and self.startStepsButton.isVisible():
            self.startStepsButton.setFocus()

        # update progress bars
        self._updateProgressBars(False)
        self.overallProgressBar.setValue(0)
        self.currentProgressBar.setValue(0)

    def blinkStart(self, success):
        self.blinkResult = success
        self.blinkTimer.start(500)
        self.blinkSwitch = True

    def blinkStop(self):
        self.blinkTimer.stop()
        self.serialNumberLabel.setStyleSheet("QLabel { }")

    def drawLastAttempts(self, attempts):
        # clear layout
        item = self.lastResultsLayout.takeAt(0)
        while item:
            widget = item.widget()
            if widget:
                widget.setParent(None)
            item = self.lastResultsLayout.takeAt(0)

        # prepare to draw
        to_draw = []
        for attempt in attempts:
            if attempt is None:
                to_draw.append(MainWindow.WORK_STATE_UNKNOWN)
            elif attempt is True:
                to_draw.append(MainWindow.WORK_STATE_PASSED)
            elif attempt is False:
                to_draw.append(MainWindow.WORK_STATE_FAILED)

        # prepare to status icons
        for state in to_draw:
            self.lastResultsLayout.addWidget(
                self._statusToWidget(self.lastResultsLayout.parentWidget(), state))

        # if all elements are False set the needed label to visible
        self.checkNeededLabel.setVisible(
            False if [e for e in attempts if e is not False] else True)

    def blinkTitle(self):
        if self.blinkSwitch:
            color = "lightgreen" if self.blinkResult else "red"
            self.serialNumberLabel.setStyleSheet("QLabel { background-color : %s; }" % color)
            self.blinkSwitch = False
        else:
            self.serialNumberLabel.setStyleSheet("QLabel { }")
            self.blinkSwitch = True

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
            _removeItemFromGridLayout(layout, i, 1)
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
        if not settings.FORCE_RESCAN_BARCODE:
            self.startTestsButton.setEnabled(qApp.router.canStartTests)
            self.startStepsButton.setEnabled(qApp.router.canStartSteps)
        self.inRunningMode = False

    @QtCore.pyqtSlot()
    def switchToBarcode(self):
        # clear the error message
        self.cleanErrorMessage()

        # clear the barcode input
        self.barcodeLineEdit.clear()

        # switch to barcode
        self.stackedWidget.setCurrentWidget(self.barcodePage)

        self.workstationTestLabel.setHidden(True)

        self.blinkStop()

        # TODO clean router structure

    @QtCore.pyqtSlot()
    def checkBarcodeAndLoadRouter(self):
        # clear the error message
        self.cleanErrorMessage()

        serialNumber = self.barcodeLineEdit.text()
        try:
            # Set the router for the whole application
            self.loadRouter(qApp.useRouter(serialNumber))

            self.stackedWidget.setCurrentWidget(self.workPage)

            if int(serialNumber) in settings.WORKSTATION_TESTING_SERIALS:
                self.workstationTestLabel.setHidden(False)
            else:
                self.workstationTestLabel.setHidden(True)

        except IncorrectSerialNumber:
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
        runner.runAskUser.connect(self.displayAskUser)
        runner.runStarted.connect(self.stepStarted)
        runner.runFinished.connect(self.stepFinished)
        runner.runsFinished.connect(self.stepsFinished)
        runner.printInstructions.connect(self.printInstructions)

        self.blinkStop()

        # start runner
        if runner.performRuns():
            self._updateProgressBars(True, len(qApp.stepPlan))
            self.enterRunningMode()

    @QtCore.pyqtSlot(int)
    def updateProgress(self, value):
        self.currentProgressBar.setValue(value)

    @QtCore.pyqtSlot(str, dict, QtCore.QMutex, QtCore.QWaitCondition)
    def displayAskUser(self, msg, result, mutex, condition):
        response = QtWidgets.QMessageBox.question(
            self, u"Dotaz", msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        mutex.lock()
        result['result'] = response == QtWidgets.QMessageBox.Yes
        condition.wakeAll()
        mutex.unlock()

    @QtCore.pyqtSlot(int)
    def stepStarted(self, planIndex):
        name = qApp.workflow.WORKFLOW[qApp.stepPlan[planIndex]].name
        qApp.loggerMain.info("Starting step '%s'" % name)
        self.currentProgressBar.setValue(0)
        self.updateStep(qApp.stepPlan[planIndex], MainWindow.WORK_STATE_RUNNING)

    @QtCore.pyqtSlot(int, bool)
    def stepFinished(self, planIndex, passed):
        name = qApp.workflow.WORKFLOW[qApp.stepPlan[planIndex]].name
        msg = "Step '%s' finished - %s" % (name, ("PASSED" if passed else "FAILED"))
        qApp.loggerMain.info(msg) if passed else qApp.loggerMain.error(msg)
        state = MainWindow.WORK_STATE_PASSED if passed else MainWindow.WORK_STATE_FAILED
        self.overallProgressBar.setValue(self.overallProgressBar.value() + 1)
        self.updateStep(qApp.stepPlan[planIndex], state)
        qApp.router.storeStep(qApp.workflow.WORKFLOW[qApp.stepPlan[planIndex]].name, passed)

    @QtCore.pyqtSlot(int, int)
    def stepsFinished(self, passedCount, totalCount):
        msg = "Steps finished (%d/%d succeeded)" % (passedCount, totalCount)
        qApp.loggerMain.info(msg)
        self._updateProgressBars(False)
        qApp.router.incStepAttempt()

        if passedCount == totalCount:
            qApp.router.setRunSuccessful()

        self.exitRunningMode()
        self.blinkStart(passedCount == totalCount)

        # Store step results
        qApp.router.storeResult('S', passedCount == totalCount)

        # Handle focus
        if passedCount == totalCount or settings.FORCE_RESCAN_BARCODE:
            self.backButton.setFocus()
        else:
            self.startStepsButton.setFocus()

        # when connection fails during the run go back to scan mode
        # it would probably fail after a new code is scanned
        if qApp.router.dbFailed:
            self.switchToBarcode()

        # update attempts
        self.drawLastAttempts(getLastRunsResults())

    @QtCore.pyqtSlot(str)
    def printInstructions(self, msg):
        QtWidgets.QMessageBox.information(
            self, "Instrukce", msg
        )

    @QtCore.pyqtSlot(str)
    def setTitle(self, text=None):
        if not text:
            self.serialNumberLabel.setText("%s (%s)" % (qApp.router.id, qApp.router.idHex))
        else:
            self.serialNumberLabel.setText(text)

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
        if not qApp.run_offline:
            if qApp.connection.isOpen():
                qApp.loggerMain.info("Closing db connection.")
                qApp.connection.close()

        backupAppLog()

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
        runner.runAskUser.connect(self.displayAskUser)
        runner.runStarted.connect(self.testStarted)
        runner.runFinished.connect(self.testFinished)
        runner.runsFinished.connect(self.testsFinished)
        runner.printInstructions.connect(self.printInstructions)
        runner.setTitle.connect(self.setTitle)

        self.blinkStop()

        # start runner
        if runner.performRuns():
            self._updateProgressBars(True, len(qApp.testPlan))
            self.enterRunningMode()

    @QtCore.pyqtSlot(int)
    def testStarted(self, planIndex):
        name = qApp.tests.TESTS[qApp.testPlan[planIndex]].name
        qApp.loggerMain.info("Starting test '%s'" % name)
        self.currentProgressBar.setValue(0)
        self.updateTest(qApp.testPlan[planIndex], MainWindow.WORK_STATE_RUNNING)

    @QtCore.pyqtSlot(int, bool)
    def testFinished(self, planIndex, passed):
        name = qApp.tests.TESTS[qApp.testPlan[planIndex]].name
        msg = "Test '%s' finished - %s" % (name, ("PASSED" if passed else "FAILED"))
        qApp.loggerMain.info(msg) if passed else qApp.loggerMain.error(msg)
        state = MainWindow.WORK_STATE_PASSED if passed else MainWindow.WORK_STATE_FAILED
        self.overallProgressBar.setValue(self.overallProgressBar.value() + 1)
        self.updateTest(qApp.testPlan[planIndex], state)
        qApp.router.storeTest(qApp.tests.TESTS[qApp.testPlan[planIndex]].name, passed)

    @QtCore.pyqtSlot(int, int)
    def testsFinished(self, passedCount, totalCount):
        msg = "Tests finished (%d/%d succeeded)" % (passedCount, totalCount)
        qApp.loggerMain.info(msg)
        self._updateProgressBars(False)
        qApp.router.incTestAttempt()
        if passedCount == totalCount:
            qApp.router.setRunSuccessful()

        self.exitRunningMode()
        self.blinkStart(passedCount == totalCount)

        # Store step results
        qApp.router.storeResult('T', passedCount == totalCount)

        # Handle focus
        if passedCount == totalCount or settings.FORCE_RESCAN_BARCODE:
            self.backButton.setFocus()
        else:
            self.startTestsButton.setFocus()

        # when connection fails during the run go back to scan mode
        # it would probably fail after a new code is scanned
        if qApp.router.dbFailed:
            self.switchToBarcode()

        # update attempts
        self.drawLastAttempts(getLastRunsResults())
