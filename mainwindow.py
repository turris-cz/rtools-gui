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

            # TODO this is just some sample remove it afterwards
            #router.storeStep(workflow.WORKFLOW[1].name, True)
            #router.storeTest(tests.TESTS[1].name, True)
            self.updateTest(0, MainWindow.WORK_STATE_PASSED)
            self.updateTest(1, MainWindow.WORK_STATE_FAILED)
            self.updateTest(2, MainWindow.WORK_STATE_PASSED)
            self.updateTest(3, MainWindow.WORK_STATE_RUNNING)
        else:
            self.errorLabel.setText(u"'%s' je neplatné!" % serialNumber)

    def closeEvent(self, event):

        # close the database
        if qApp.connection.isOpen():
            qApp.connection.close()

        event.accept()
