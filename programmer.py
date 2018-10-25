# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.programmer import Ui_Programmer

from utils import MAX_SERIAL_LEN

from application import qApp, settings
from moxtester import MoxTester, MoxTesterException
from workflow import WorkFlow, WorkflowException


class ProgrammerWidget(QtWidgets.QFrame, Ui_Programmer):
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

    def __init__(self, mainWindow, index):
        self.mainWindow = mainWindow
        self.index = index

        super(ProgrammerWidget, self).__init__()
        self.setupUi(self)  # create gui
        self.barcodeLineEdit.setMaxLength(MAX_SERIAL_LEN)
        self.indexLabel.setText("Programátor: " + str(index + 1))
        self.intro_error(None)

        self.workflow = None  # Current workflow for this programmer
        self.programmer = None  # Handle for MoxTester
        self.connectProgrammer()

    def intro_error(self, message):
        "Display error for intro page. Pass None to reset previous error."
        self.introMessageLabel.setVisible(message is None)
        self.introErrorLabel.setVisible(message is not None)
        if message is not None:
            self.introErrorLabel.setText(message)

    def select(self):
        "Try to select this programmer for new board session"
        if self.programmer is None:
            self.mainWindow.display_msg(
                "Programátor {} zřejmě není připojen".format(self.index + 1))
            return
        if self.workflow is not None:
            self.mainWindow.display_msg(
                "Programátor {} je aktuálně obsazen".format(self.index + 1))
            return
        self.programmer.reset_tester()
        if not self.programmer.board_present():
            self.mainWindow.display_msg(
                "Do programátoru {} není vložená deska".format(self.index + 1))
            return
        self.introWidget.setCurrentWidget(self.pageIntroSerial)
        self.barcodeLineEdit.setFocus()

    @QtCore.pyqtSlot()
    def connectProgrammer(self):
        try:
            self.programmer = MoxTester(self.index)
            self.programmer.selftest()
        except MoxTesterException:
            # TODO print error to log
            # Ok this failed so we don't have programmer
            pass
        if self.programmer is not None:
            self.introWidget.setCurrentWidget(self.pageIntroReady)

    @QtCore.pyqtSlot()
    def barcodeScanEnter(self):
        """Slot called when barcode is scanned to input box. Should check if
        given code is valid and start flashing process"""
        serial_number = int(self.barcodeLineEdit.text())
        self.barcodeLineEdit.clear()
        self.mainWindow.refocus()
        if (serial_number >> 32) == 0xFFFFFFFF:
            self.intro_error("Naskenován kód programátoru")
            self.introWidget.setCurrentWidget(self.pageIntroReady)
            return
        try:
            self.workflow = WorkFlow(None, self.programmer, serial_number)
        except WorkflowException as e:
            self.workflow = None
            self.intro_error(str(e))
            self.introWidget.setCurrentWidget(self.pageIntroReady)
            return

        self.serialNumberLabel.setText(hex(serial_number))
        self.typeLabel.setText(self.workflow.get_board_name())
        # TODO load workflow to gui
        self.contentWidget.setCurrentWidget(self.pageWork)

    @QtCore.pyqtSlot()
    def barcodeAbandon(self):
        """Slot called when input box for barcode is abandoned. It closes
        current state and returns to intro page"""
        self.barcodeLineEdit.clear()
        self.introWidget.setCurrentWidget(self.pageIntroReady)
        self.mainWindow.refocus()
