#!/usr/bin/env python2
# coding=utf-8

import sys
from PyQt4 import QtGui, QtCore

from gui.gui_barcodechecker import Ui_BarcodeCheckerWindow

from instalator import serialNumberValidator as isValidSerial


class BarcodeChecker(QtGui.QMainWindow, Ui_BarcodeCheckerWindow):
    def __init__(self):
        super(BarcodeChecker, self).__init__()
        self.setupUi(self)
        from gui import uiresources
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.edit1.returnPressed.connect(self.edit1filled)
        self.edit2.returnPressed.connect(self.edit2filled)
        self.initialize()

    def initialize(self):
        self.scanningDone = False
        self.edit1.clear()
        self.edit2.clear()
        self.setNormalStatus(u"Načtěte první kód.")
        self.edit1.setFocus()

    @QtCore.pyqtSlot()
    def edit1filled(self):
        cleaned = self.cleanupBarcode(self.edit1.text())
        self.edit1.setText(cleaned)
        if isValidSerial(cleaned):
            self.setNormalStatus(u"První kód je v pořádku, načtěte druhý kód.")
            self.edit2.setFocus()
        else:
            self.setErrorStatus(u"První sériové číslo (%s) není platné.<br>Zkuste ho načíst znovu." % cleaned)
            self.edit1.clear()

    @QtCore.pyqtSlot()
    def edit2filled(self):
        if self.scanningDone:
            self.initialize()
            return

        cleaned = self.cleanupBarcode(self.edit2.text())
        self.edit2.setText(cleaned)
        if isValidSerial(cleaned):
            self.doComparison()
        else:
            self.setErrorStatus(u"Druhé sériové číslo (%s) není platné.<br>Zkuste ho načíst znovu." % cleaned)
            self.edit2.clear()

    def doComparison(self):
        code1 = self.edit1.text()
        code2 = self.edit2.text()
        if code1 == code2:
            self.scanningDone = True
            self.setSuccessStatus(u"Vše je v pořádku, kódy se shodují.<br>Pro nový start načtěte jakýkoliv kód nebo stiskněte Enter.")
        else:
            self.setErrorStatus(u"Chyba! Kódy se neshodují.")
            self.showCriticalError(u"Kódy se neshodují, pravděpodobně nevkládáte router do správné krabice, případně byla do skříně vložena špatná deska.<br><br>"
                                   u"Chyba také může být způsobena špatným načtením jednoho z kódů, zkuste kontrolu provést důkladně ještě jednou.")
            self.initialize()

    def cleanupBarcode(self, barcode):
        barcode = unicode(barcode).strip()
        # i'm too lazy to switch layout every time...
        cz_to_en_keys = {u'+': "1", u'ě': "2", u'š': "3", u'č': "4", u'ř': "5",
                         u'ž': "6", u'ý': "7", u'á': "8", u'í': "9", u'é': "0"}
        return reduce(lambda x, y: x.replace(y, cz_to_en_keys[y]), cz_to_en_keys, barcode)

    def setErrorStatus(self, text):
        self.labelStatus.setText(text)
        self.labelStatus.setStyleSheet("QLabel {color: red;}")

    def setNormalStatus(self, text):
        self.labelStatus.setText(text)
        self.labelStatus.setStyleSheet("")

    def setSuccessStatus(self, text):
        self.labelStatus.setText(text)
        self.labelStatus.setStyleSheet("QLabel {color: #092;}")

    def showCriticalError(self, msg):
        return QtGui.QMessageBox.critical(None, u"Chyba!", msg, QtGui.QMessageBox.Ok)


def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = BarcodeChecker()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
