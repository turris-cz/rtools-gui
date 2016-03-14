# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.mainwindow import Ui_MainWindow

from custom_exceptions import DbError
from utils import serialNumberValidator, MAX_SERIAL_LEN

# Include settings
from application import workflow, tests, qApp
from runner import Runner

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
        if not qApp.connection.open():
            # TODO display a message perhaps
            raise DbError(qApp.connection.lastError().text())

    def loadRouter(self, router):
        # Set title
        self.serialNumberLabel.setText(router.id + " (%016x)" % int(router.id))

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

    def cleanErrorMessage(self):
        self.errorLabel.setText("")

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
        # filter workflow (skipped passed
        self.stepPlan = [
            i for i in range(len(workflow.WORKFLOW))
            if not workflow.WORKFLOW[i].name in qApp.router.performedSteps['passed']
        ]

        # Everything was performed. Skipping
        if not self.stepPlan:
            # TODO logging
            print "All steps were performed for router '%s'" % qApp.router.id
            return

        # Note that runner needs to be a object member
        # otherwise it would be disposed its thread execution
        self.runner = Runner([workflow.WORKFLOW[i] for i in self.stepPlan])

        # connect signals
        self.runner.runProgress.connect(self.updateProgress)
        self.runner.runStarted.connect(self.stepStarted)
        self.runner.runFinished.connect(self.stepFinished)
        self.runner.runsFinished.connect(self.stepsFinished)

        # update progress bars
        self.currentProgressBar.setEnabled(True)
        self.overallProgressBar.setEnabled(True)
        self.overallProgressBar.setMaximum(len(self.stepPlan))
        self.overallProgressBar.setValue(0)

        # start runner
        self.runner.performRuns()

    @QtCore.pyqtSlot(int)
    def updateProgress(self, value):
        self.currentProgressBar.setValue(self.currentProgressBar.value() + value)

    @QtCore.pyqtSlot(int)
    def stepStarted(self, planIndex):
        # TODO log
        print "Starting step", workflow.WORKFLOW[self.stepPlan[planIndex]].name
        self.currentProgressBar.setValue(0)
        self.updateStep(self.stepPlan[planIndex], MainWindow.WORK_STATE_RUNNING)

    @QtCore.pyqtSlot(int, bool)
    def stepFinished(self, planIndex, passed):
        # TODO log
        print "Finished step", workflow.WORKFLOW[self.stepPlan[planIndex]].name, passed
        state = MainWindow.WORK_STATE_PASSED if passed else MainWindow.WORK_STATE_FAILED
        self.overallProgressBar.setValue(self.overallProgressBar.value() + 1)
        self.updateStep(self.stepPlan[planIndex], state)
        qApp.router.storeStep(workflow.WORKFLOW[self.stepPlan[planIndex]].name, passed)

    @QtCore.pyqtSlot()
    def stepsFinished(self):
        print "All steps finished"
        self.currentProgressBar.setEnabled(False)
        self.currentProgressBar.setValue(0)
        self.overallProgressBar.setEnabled(False)
        self.overallProgressBar.setValue(0)
        qApp.router.incStepAttempt()

    def closeEvent(self, event):

        # close the database
        if qApp.connection.isOpen():
            qApp.connection.close()

        event.accept()

    @QtCore.pyqtSlot()
    def runTests(self):
        # prepare the plan
        self.testPlan = range(len(tests.TESTS))

        # Note that runner needs to be a object member
        # otherwise it would be disposed its thread execution
        self.runner = Runner([tests.TESTS[i] for i in self.testPlan])

        # connect signals
        self.runner.runProgress.connect(self.updateProgress)
        self.runner.runStarted.connect(self.testStarted)
        self.runner.runFinished.connect(self.testFinished)
        self.runner.runsFinished.connect(self.testsFinished)

        # update progress bars
        self.currentProgressBar.setEnabled(True)
        self.overallProgressBar.setEnabled(True)
        self.overallProgressBar.setMaximum(len(self.testPlan))
        self.overallProgressBar.setValue(0)

        # start runner
        self.runner.performRuns()

    @QtCore.pyqtSlot(int)
    def testStarted(self, planIndex):
        # TODO log
        print "Starting test", workflow.WORKFLOW[self.testPlan[planIndex]].name
        self.currentProgressBar.setValue(0)
        self.updateTest(self.testPlan[planIndex], MainWindow.WORK_STATE_RUNNING)

    @QtCore.pyqtSlot(int, bool)
    def testFinished(self, planIndex, passed):
        # TODO log
        print "Finished test", workflow.WORKFLOW[self.testPlan[planIndex]].name, passed
        state = MainWindow.WORK_STATE_PASSED if passed else MainWindow.WORK_STATE_FAILED
        self.overallProgressBar.setValue(self.overallProgressBar.value() + 1)
        self.updateTest(self.testPlan[planIndex], state)
        qApp.router.storeTest(tests.TESTS[self.testPlan[planIndex]].name, passed)

    @QtCore.pyqtSlot()
    def testsFinished(self):
        print "All tests finished"
        self.currentProgressBar.setEnabled(False)
        self.currentProgressBar.setValue(0)
        self.overallProgressBar.setEnabled(False)
        self.overallProgressBar.setValue(0)
        qApp.router.incTestAttempt()
