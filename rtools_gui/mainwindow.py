# -*- coding: utf8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from .ui.mainwindow import Ui_MainWindow

from .custom_exceptions import DbError, IncorrectSerialNumber
from .utils import MAX_SERIAL_LEN

from .programmer import ProgrammerWidget


def _removeItemFromGridLayout(layout, row, column):
    item = layout.itemAtPosition(row, column)
    if item:
        layout.removeItem(item)
        item.widget().hide()
        item.widget().deleteLater()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, dbconnection, resources):
        super(MainWindow, self).__init__()
        self.setupUi(self)  # create gui
        self.barcodeLineEdit.setMaxLength(MAX_SERIAL_LEN)
        self.error_label.setVisible(False)

        self.programmers = [None]*4
        for i in range(4):
            self.programmers[i] = ProgrammerWidget(self, resources, i)
            self.programmersLayout.addWidget(
                self.programmers[i], i // 2, i % 2)

    def refocus(self):
        "Set focus back to primary window input box."
        self.barcodeLineEdit.setFocus()

    def display_msg(self, message):
        """"Display given message in main window message box. You can pass None
        as a message to clear error box."""
        if message is None:
            self.error_label.setVisible(False)
        else:
            self.error_label.setVisible(True)
            self.error_label.setText(message)

    @QtCore.pyqtSlot()
    def barcodeScanEnter(self):
        "Slot called when text is entered to primary text field in main window"
        self.display_msg(None)
        serial_number = int(self.barcodeLineEdit.text())
        index = serial_number & 0xFFFFFFFF
        if (serial_number >> 32) != 0xFFFFFFFF or index < 0 or index > 3:
            self.barcodeLineEdit.clear()
            self.display_msg(
                "Naskenovaný kód není validní pro volbu programátoru")
            return
        self.programmers[index].select()
        self.barcodeLineEdit.clear()
