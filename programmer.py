# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from ui.programmer import Ui_Programmer

from utils import MAX_SERIAL_LEN

from application import qApp, settings


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

        # TODO try to connect to programmer

        self.inRunningMode = False

    def select(self):
        # TODO check of we have connected programmer
        self.introWidget.setCurrentWidget(self.pageIntroSerial)
        self.barcodeLineEdit.setFocus()

    @QtCore.pyqtSlot()
    def connectProgrammer(self):
        # TODO for now just switch to active
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
