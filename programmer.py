# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.programmer import Ui_Programmer

from utils import MAX_SERIAL_LEN

from application import qApp, settings
from moxtester import MoxTester, MoxTesterException


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

        self.programmer = None
        self.connectProgrammer()

    def select(self):
        "Try to select this programmer for new board session"
        if self.programmer is None:
            self.mainWindow.display_msg(
                "Programátor {} zřejmě není připojen".format(self.index))
            return
        # TODO check if we are not already running some
        self.programmer.reset_tester()
        if not self.programmer.board_present():
            self.mainWindow.display_msg(
                "Do programátoru {} není vložená deska".format(self.index))
            return
        self.introWidget.setCurrentWidget(self.pageIntroSerial)
        self.barcodeLineEdit.setFocus()

    @QtCore.pyqtSlot()
    def connectProgrammer(self):
        try:
            # TODO use real id (serial number like)
            self.programmer = MoxTester(self.index)
        except MoxTesterException:
            # Ok this failed so we don't have programmer
            pass
        if self.programmer is not None:
            self.introWidget.setCurrentWidget(self.pageIntroReady)

    @QtCore.pyqtSlot()
    def barcodeScanEnter(self):
        # TODO verify state and switch
        print(int(self.barcodeLineEdit.text()))
        self.serialNumberLabel.setText(self.barcodeLineEdit.text())
        # TODO set type
        # TODO set serial number to programmator state
        self.barcodeLineEdit.clear()
        self.contentWidget.setCurrentWidget(self.pageWork)

    @QtCore.pyqtSlot()
    def barcodeAbandon(self):
        # TODO verify state and switch
        self.barcodeLineEdit.clear()
        self.introWidget.setCurrentWidget(self.pageIntroReady)
        self.mainWindow.refocus()
