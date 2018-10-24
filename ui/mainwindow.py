# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(885, 646)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.programmersLayout = QtWidgets.QGridLayout()
        self.programmersLayout.setObjectName("programmersLayout")
        self.verticalLayout.addLayout(self.programmersLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.programmerLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.programmerLabel.setFont(font)
        self.programmerLabel.setObjectName("programmerLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.programmerLabel)
        self.barcodeLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.barcodeLineEdit.setFont(font)
        self.barcodeLineEdit.setObjectName("barcodeLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.barcodeLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.error_label = QtWidgets.QLabel(self.centralwidget)
        self.error_label.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.error_label.setFont(font)
        self.error_label.setAutoFillBackground(False)
        self.error_label.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.error_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setObjectName("error_label")
        self.verticalLayout.addWidget(self.error_label)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 885, 22))
        self.menubar.setObjectName("menubar")
        self.menuMode = QtWidgets.QMenu(self.menubar)
        self.menuMode.setObjectName("menuMode")
        MainWindow.setMenuBar(self.menubar)
        self.actionManu_ln_Testovac = QtWidgets.QAction(MainWindow)
        self.actionManu_ln_Testovac.setObjectName("actionManu_ln_Testovac")
        self.actionProduk_n = QtWidgets.QAction(MainWindow)
        self.actionProduk_n.setObjectName("actionProduk_n")
        self.actionTest_stanovi_t = QtWidgets.QAction(MainWindow)
        self.actionTest_stanovi_t.setObjectName("actionTest_stanovi_t")
        self.menuMode.addAction(self.actionProduk_n)
        self.menuMode.addAction(self.actionTest_stanovi_t)
        self.menuMode.addSeparator()
        self.menuMode.addAction(self.actionManu_ln_Testovac)
        self.menubar.addAction(self.menuMode.menuAction())

        self.retranslateUi(MainWindow)
        self.barcodeLineEdit.returnPressed.connect(MainWindow.barcodeScanEnter)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Turris MOX - Router tool GUI"))
        self.programmerLabel.setText(_translate("MainWindow", "Naskenujte kód programátoru:"))
        self.error_label.setText(_translate("MainWindow", "ERROR MESSAGE"))
        self.menuMode.setTitle(_translate("MainWindow", "Mód"))
        self.actionManu_ln_Testovac.setText(_translate("MainWindow", "Manuální"))
        self.actionProduk_n.setText(_translate("MainWindow", "Produkční"))
        self.actionTest_stanovi_t.setText(_translate("MainWindow", "Test stanoviště"))

from qrc import icons
