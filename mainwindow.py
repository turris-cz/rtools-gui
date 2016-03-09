# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore
from ui.mainwindow import Ui_MainWindow

from utils import serialNumberValidator, MAX_SERIAL_LEN

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)  # create gui
        self.barcodeLineEdit.setMaxLength(MAX_SERIAL_LEN)

    def cleanErrorMessage(self):
        self.errorLabel.setText("")

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

        if serialNumberValidator(self.barcodeLineEdit.text()):
            # TODO load or create structure from DB and set the page
            self.stackedWidget.setCurrentWidget(self.workPage)
        else:
            self.errorLabel.setText(u"'%s' je neplatné!" % self.barcodeLineEdit.text())
