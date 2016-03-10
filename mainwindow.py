# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.mainwindow import Ui_MainWindow

from utils import serialNumberValidator, MAX_SERIAL_LEN

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


# TODO create a proper workflow
class Element(object):
    def __init__(self, name):
        self.name = name

WORKFLOW = (
    Element("POWER"),
    Element("ATSHA"),
    Element("UBOOT"),
    Element("REBOOT"),
    Element("REFLASH"),
    Element("RTC"),
)

TESTS = (
    Element("USB"),
    Element("PCIA"),
    Element("THERMOMETER"),
    Element("GPIO"),
    Element("CLOCK"),
)

def _removeItemFromGridLayout(layout, row, column):
    item = layout.itemAtPosition(row, column)
    item and layout.removeItem(item)
    return item

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

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

        # TODO names shall be read from db
        workflow_len = len(WORKFLOW)
        for i in range(workflow_len):
            self.addStep(i, WORKFLOW[i].name)
        # add spacers
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stepsLayout.addItem(spacer, workflow_len, 0)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stepsLayout.addItem(spacer, workflow_len, 1)

        # TODO names shall be read from db
        tests_len = len(TESTS)
        for i in range(tests_len):
            self.addTest(i, TESTS[i].name)
        # add spacers
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.testsLayout.addItem(spacer, tests_len, 0)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.testsLayout.addItem(spacer, tests_len, 1)

    def cleanErrorMessage(self):
        self.errorLabel.setText("")

    def _statusToWidget(self, parent, status):
        if status == WORK_STATE_UNKNOWN:
            widget = QtWidgets.QLabel(parent)
            widget.setPixmap(
                QtWidgets.QApplication.style().standardIcon(
                    QtWidgets.QStyle.SP_TitleBarContextHelpButton
                ).pixmap(20, 20)
            )
        elif status == WORK_STATE_PASSED:
            widget = QtWidgets.QLabel(parent)
            widget.setPixmap(
                QtWidgets.QApplication.style().standardIcon(
                    QtWidgets.QStyle.SP_DialogApplyButton
                ).pixmap(20, 20)
            )
        elif status == WORK_STATE_FAILED:
            widget = QtWidgets.QLabel(parent)
            widget.setPixmap(
                QtWidgets.QApplication.style().standardIcon(
                    QtWidgets.QStyle.SP_DialogCloseButton
                ).pixmap(20, 20)
            )
        elif status == WORK_STATE_RUNNING:
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
        self._addElement(self.stepsLayout, i, text, WORK_STATE_UNKNOWN)

    def updateStep(self, i, status):
        self._updateElement(self.stepsLayout, i, status)

    def addTest(self, i, text):
        self._addElement(self.testsLayout, i, text, WORK_STATE_UNKNOWN)

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
            # TODO load or create structure from DB and set the page
            self.stackedWidget.setCurrentWidget(self.workPage)

            # TODO this is just a sample remove it
            self.serialNumberLabel.setText(serialNumber +  " (%016x)" % int(serialNumber))
            self.updateStep(0, WORK_STATE_PASSED)
            self.updateStep(1, WORK_STATE_PASSED)
            self.updateStep(2, WORK_STATE_PASSED)
            self.updateStep(3, WORK_STATE_PASSED)
            self.updateStep(4, WORK_STATE_PASSED)
            self.updateStep(5, WORK_STATE_PASSED)

            self.updateTest(0, WORK_STATE_PASSED)
            self.updateTest(1, WORK_STATE_FAILED)
            self.updateTest(2, WORK_STATE_PASSED)
            self.updateTest(3, WORK_STATE_RUNNING)
        else:
            self.errorLabel.setText(u"'%s' je neplatné!" % serialNumber)
