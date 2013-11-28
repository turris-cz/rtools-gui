# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'formstatview.ui'
#
# Created: Thu Nov 14 17:19:44 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_StatusChecker(object):
    def setupUi(self, StatusChecker):
        StatusChecker.setObjectName(_fromUtf8("StatusChecker"))
        StatusChecker.resize(500, 500)
        self.verticalLayout = QtGui.QVBoxLayout(StatusChecker)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(StatusChecker)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.label_3 = QtGui.QLabel(StatusChecker)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(StatusChecker)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit = QtGui.QLineEdit(StatusChecker)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(StatusChecker)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.outBox = QtGui.QLabel(StatusChecker)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.outBox.sizePolicy().hasHeightForWidth())
        self.outBox.setSizePolicy(sizePolicy)
        self.outBox.setText(_fromUtf8(""))
        self.outBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.outBox.setObjectName(_fromUtf8("outBox"))
        self.verticalLayout.addWidget(self.outBox)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.pushButton_2 = QtGui.QPushButton(StatusChecker)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(StatusChecker)
        QtCore.QMetaObject.connectSlotsByName(StatusChecker)

    def retranslateUi(self, StatusChecker):
        StatusChecker.setWindowTitle(_translate("StatusChecker", "Router status", None))
        self.label.setText(_translate("StatusChecker", "<h1>Flashing status</h1>", None))
        self.label_3.setText(_translate("StatusChecker", "Naskenujte čárový kód do následuícího políčka a zobrazí se Vám status, s jakým byl daný router naflashován a případne chybová hláška, když byl naflashován neúspěšně.\n"
"Když chcete zobrazit kompletní log všech routrů, klikněte na tlačítko \"Log všech routrů\".", None))
        self.label_2.setText(_translate("StatusChecker", "Router id", None))
        self.pushButton.setText(_translate("StatusChecker", "Ukázat status", None))
        self.pushButton_2.setText(_translate("StatusChecker", "Log všech routrů", None))

