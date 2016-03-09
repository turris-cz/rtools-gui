# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/barcodechecker.ui'
#
# Created: Wed Dec 11 15:21:39 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_BarcodeCheckerWindow(object):
    def setupUi(self, BarcodeCheckerWindow):
        BarcodeCheckerWindow.setObjectName(_fromUtf8("BarcodeCheckerWindow"))
        BarcodeCheckerWindow.resize(512, 207)
        BarcodeCheckerWindow.setAutoFillBackground(False)
        self.centralwidget = QtGui.QWidget(BarcodeCheckerWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelTitle = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.labelTitle.setFont(font)
        self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTitle.setObjectName(_fromUtf8("labelTitle"))
        self.verticalLayout.addWidget(self.labelTitle)
        self.labelStatus = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelStatus.setFont(font)
        self.labelStatus.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.verticalLayout.addWidget(self.labelStatus)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label1 = QtGui.QLabel(self.centralwidget)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label1)
        self.label2 = QtGui.QLabel(self.centralwidget)
        self.label2.setObjectName(_fromUtf8("label2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label2)
        self.edit1 = QtGui.QLineEdit(self.centralwidget)
        self.edit1.setMaxLength(11)
        self.edit1.setObjectName(_fromUtf8("edit1"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edit1)
        self.edit2 = QtGui.QLineEdit(self.centralwidget)
        self.edit2.setMaxLength(11)
        self.edit2.setObjectName(_fromUtf8("edit2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edit2)
        self.verticalLayout.addLayout(self.formLayout)
        BarcodeCheckerWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(BarcodeCheckerWindow)
        QtCore.QMetaObject.connectSlotsByName(BarcodeCheckerWindow)

    def retranslateUi(self, BarcodeCheckerWindow):
        BarcodeCheckerWindow.setWindowTitle(_translate("BarcodeCheckerWindow", "Kontrola čárových kódů", None))
        self.labelTitle.setText(_translate("BarcodeCheckerWindow", "Kontrola čárových kódů", None))
        self.labelStatus.setText(_translate("BarcodeCheckerWindow", "Instrukce.", None))
        self.label1.setText(_translate("BarcodeCheckerWindow", "První kód", None))
        self.label2.setText(_translate("BarcodeCheckerWindow", "Druhý kód", None))

