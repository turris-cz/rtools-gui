# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Window(object):
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.resize(885, 646)
        self.centralwidget = QtWidgets.QWidget(Window)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.programmersLayout = QtWidgets.QGridLayout()
        self.programmersLayout.setObjectName("programmersLayout")
        self.verticalLayout_2.addLayout(self.programmersLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.programmerLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.programmerLabel.setFont(font)
        self.programmerLabel.setObjectName("programmerLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.programmerLabel)
        self.barcodeLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.barcodeLineEdit.setFont(font)
        self.barcodeLineEdit.setObjectName("barcodeLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.barcodeLineEdit)
        self.verticalLayout_2.addLayout(self.formLayout)
        Window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 885, 22))
        self.menubar.setObjectName("menubar")
        self.menuMode = QtWidgets.QMenu(self.menubar)
        self.menuMode.setObjectName("menuMode")
        Window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Window)
        self.statusbar.setObjectName("statusbar")
        Window.setStatusBar(self.statusbar)
        self.actionManu_ln_Testovac = QtWidgets.QAction(Window)
        self.actionManu_ln_Testovac.setObjectName("actionManu_ln_Testovac")
        self.actionProduk_n = QtWidgets.QAction(Window)
        self.actionProduk_n.setObjectName("actionProduk_n")
        self.actionTest_stanovi_t = QtWidgets.QAction(Window)
        self.actionTest_stanovi_t.setObjectName("actionTest_stanovi_t")
        self.menuMode.addAction(self.actionProduk_n)
        self.menuMode.addAction(self.actionTest_stanovi_t)
        self.menuMode.addSeparator()
        self.menuMode.addAction(self.actionManu_ln_Testovac)
        self.menubar.addAction(self.menuMode.menuAction())

        self.retranslateUi(Window)
        self.barcodeLineEdit.returnPressed.connect(Window.barcodeScanEnter)
        QtCore.QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        _translate = QtCore.QCoreApplication.translate
        Window.setWindowTitle(_translate("Window", "Turris MOX - Router tool GUI"))
        self.programmerLabel.setText(_translate("Window", "Naskenujte kód programátoru:"))
        self.menuMode.setTitle(_translate("Window", "Mód"))
        self.actionManu_ln_Testovac.setText(_translate("Window", "Manuální"))
        self.actionProduk_n.setText(_translate("Window", "Produkční"))
        self.actionTest_stanovi_t.setText(_translate("Window", "Test stanoviště"))

from qrc import icons
