# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'installer.ui'
#
# Created: Wed Dec  4 14:22:24 2013
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

class Ui_Installer(object):
    def setupUi(self, Installer):
        Installer.setObjectName(_fromUtf8("Installer"))
        Installer.resize(500, 500)
        Installer.setMinimumSize(QtCore.QSize(250, 250))
        self.verticalLayout = QtGui.QVBoxLayout(Installer)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.stackedWidget = QtGui.QStackedWidget(Installer)
        self.stackedWidget.setEnabled(True)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.startPage = QtGui.QWidget()
        self.startPage.setObjectName(_fromUtf8("startPage"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.startPage)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.startPage)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.label_8 = QtGui.QLabel(self.startPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout_2.addWidget(self.label_8)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.startToScan = QtGui.QPushButton(self.startPage)
        self.startToScan.setObjectName(_fromUtf8("startToScan"))
        self.horizontalLayout.addWidget(self.startToScan)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.stackedWidget.addWidget(self.startPage)
        self.stepScan = QtGui.QWidget()
        self.stepScan.setObjectName(_fromUtf8("stepScan"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.stepScan)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.stepScan)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.label_5 = QtGui.QLabel(self.stepScan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setTextFormat(QtCore.Qt.PlainText)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_3.addWidget(self.label_5)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_4 = QtGui.QLabel(self.stepScan)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.lineEdit = QtGui.QLineEdit(self.stepScan)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.scanToOne = QtGui.QPushButton(self.stepScan)
        self.scanToOne.setObjectName(_fromUtf8("scanToOne"))
        self.horizontalLayout_3.addWidget(self.scanToOne)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.stackedWidget.addWidget(self.stepScan)
        self.stepOne = QtGui.QWidget()
        self.stepOne.setObjectName(_fromUtf8("stepOne"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.stepOne)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label_15 = QtGui.QLabel(self.stepOne)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.verticalLayout_8.addWidget(self.label_15)
        self.label_16 = QtGui.QLabel(self.stepOne)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setWordWrap(True)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.verticalLayout_8.addWidget(self.label_16)
        self.progressBar = QtGui.QProgressBar(self.stepOne)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout_8.addWidget(self.progressBar)
        self.stackedWidget.addWidget(self.stepOne)
        self.stepTwo = QtGui.QWidget()
        self.stepTwo.setObjectName(_fromUtf8("stepTwo"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.stepTwo)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_6 = QtGui.QLabel(self.stepTwo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_4.addWidget(self.label_6)
        self.label_7 = QtGui.QLabel(self.stepTwo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_4.addWidget(self.label_7)
        self.progressBar_2 = QtGui.QProgressBar(self.stepTwo)
        self.progressBar_2.setMinimum(0)
        self.progressBar_2.setMaximum(0)
        self.progressBar_2.setProperty("value", -1)
        self.progressBar_2.setObjectName(_fromUtf8("progressBar_2"))
        self.verticalLayout_4.addWidget(self.progressBar_2)
        self.stackedWidget.addWidget(self.stepTwo)
        self.stepThree = QtGui.QWidget()
        self.stepThree.setObjectName(_fromUtf8("stepThree"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.stepThree)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.label_9 = QtGui.QLabel(self.stepThree)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout_6.addWidget(self.label_9)
        self.label_10 = QtGui.QLabel(self.stepThree)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setWordWrap(True)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.verticalLayout_6.addWidget(self.label_10)
        self.progressBar_3 = QtGui.QProgressBar(self.stepThree)
        self.progressBar_3.setMinimum(0)
        self.progressBar_3.setMaximum(0)
        self.progressBar_3.setProperty("value", 0)
        self.progressBar_3.setObjectName(_fromUtf8("progressBar_3"))
        self.verticalLayout_6.addWidget(self.progressBar_3)
        self.stackedWidget.addWidget(self.stepThree)
        self.stepFinal = QtGui.QWidget()
        self.stepFinal.setObjectName(_fromUtf8("stepFinal"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.stepFinal)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_11 = QtGui.QLabel(self.stepFinal)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_7.addWidget(self.label_11)
        self.label_12 = QtGui.QLabel(self.stepFinal)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setWordWrap(True)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.verticalLayout_7.addWidget(self.label_12)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
        self.finalToScan = QtGui.QPushButton(self.stepFinal)
        self.finalToScan.setObjectName(_fromUtf8("finalToScan"))
        self.horizontalLayout_7.addWidget(self.finalToScan)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.stackedWidget.addWidget(self.stepFinal)
        self.checkCableErrorPage = QtGui.QWidget()
        self.checkCableErrorPage.setObjectName(_fromUtf8("checkCableErrorPage"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.checkCableErrorPage)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.label_17 = QtGui.QLabel(self.checkCableErrorPage)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.verticalLayout_9.addWidget(self.label_17)
        self.tmpErrMsg = QtGui.QLabel(self.checkCableErrorPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tmpErrMsg.sizePolicy().hasHeightForWidth())
        self.tmpErrMsg.setSizePolicy(sizePolicy)
        self.tmpErrMsg.setWordWrap(True)
        self.tmpErrMsg.setObjectName(_fromUtf8("tmpErrMsg"))
        self.verticalLayout_9.addWidget(self.tmpErrMsg)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.chckToStepX = QtGui.QPushButton(self.checkCableErrorPage)
        self.chckToStepX.setObjectName(_fromUtf8("chckToStepX"))
        self.horizontalLayout_4.addWidget(self.chckToStepX)
        self.verticalLayout_9.addLayout(self.horizontalLayout_4)
        self.stackedWidget.addWidget(self.checkCableErrorPage)
        self.finalErrorPage = QtGui.QWidget()
        self.finalErrorPage.setObjectName(_fromUtf8("finalErrorPage"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.finalErrorPage)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_13 = QtGui.QLabel(self.finalErrorPage)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.verticalLayout_5.addWidget(self.label_13)
        self.label_14 = QtGui.QLabel(self.finalErrorPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setWordWrap(True)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.verticalLayout_5.addWidget(self.label_14)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.errToScan = QtGui.QPushButton(self.finalErrorPage)
        self.errToScan.setObjectName(_fromUtf8("errToScan"))
        self.horizontalLayout_6.addWidget(self.errToScan)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.stackedWidget.addWidget(self.finalErrorPage)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.label = QtGui.QLabel(Installer)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(Installer)
        QtCore.QMetaObject.connectSlotsByName(Installer)

    def retranslateUi(self, Installer):
        Installer.setWindowTitle(_translate("Installer", "Instalátor", None))
        self.label_2.setText(_translate("Installer", "<html><head/><body><p><span style=\" font-size:xx-large; font-weight:600;\">Začínáme</span></p></body></html>", None))
        self.label_8.setText(_translate("Installer", "<html><head/><body><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Připravte se psychicky na těžý úkol. Před začátkem běžte koupit basu piva, protože počas práce přijde žízeň.</li><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Vezměte jeden router.</li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Zapojte všechny kabely.</li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Oveřte, ze jsou kabely zapojené správně.</li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Klikněte na tlačítko &quot;Pokračovat&quot;<br/></li></ul></body></html>", None))
        self.startToScan.setText(_translate("Installer", "Pokračovat", None))
        self.label_3.setText(_translate("Installer", "<h1>Scan</h1>", None))
        self.label_5.setText(_translate("Installer", "Sejměte čárový kód nalepený na LAN konektoru desky routeru TURRIS.", None))
        self.label_4.setText(_translate("Installer", "Čárový kód", None))
        self.scanToOne.setText(_translate("Installer", "Spustit programovnání", None))
        self.label_15.setText(_translate("Installer", "<h1>I2C Programování</h1>", None))
        self.label_16.setText(_translate("Installer", "Praesentium molestiae sed molestias modi et impedit earum. Sint nihil sed amet dolor est eos et. Occaecati voluptatem eum autem aut voluptate.\n"
"\n"
"Vel exercitationem animi in accusantium voluptatem ea qui consequatur. Nisi explicabo aut voluptatem sit. Nisi numquam magnam rem totam. Sit sed qui omnis quis iusto.", None))
        self.label_6.setText(_translate("Installer", "<h1>CPLD Programování</h1>", None))
        self.label_7.setText(_translate("Installer", "Odio nihil placeat quibusdam repellendus labore id. Illo aut iste omnis dolore et nesciunt neque quia. Et fuga vero blanditiis maiores aut. Sequi corrupti et deserunt assumenda voluptatibus molestiae rem. Et et sequi molestias fugit.\n"
"\n"
"Quia modi rerum asperiores sapiente odio et maiores. Quo sed rem repudiandae nostrum. Quos et qui laborum iste. Est consequatur adipisci aspernatur sapiente aut ducimus. Sunt totam dignissimos eos.", None))
        self.label_9.setText(_translate("Installer", "<h1>FLASH Programování</h1>", None))
        self.label_10.setText(_translate("Installer", "Ducimus assumenda est quia. Aliquid ducimus quia aspernatur qui inventore dicta. Aut ullam ad a. Et magnam ab qui quas odit. Aperiam eos sed quibusdam non non minus unde quidem.\n"
"\n"
"Qui dolorum ut iusto facilis exercitationem. Aut voluptatem et quo voluptatem quidem a itaque aliquid. Laudantium maiores dolorem soluta dolorum. Officiis sint sapiente veniam magnam. Inventore et est voluptatem error.", None))
        self.label_11.setText(_translate("Installer", "<h1>Naprogramováno</h1>", None))
        self.label_12.setText(_translate("Installer", "Router byl úspěšně naprogramován, otevřte šampanské a jděte to zapít, pak se vraťte, odpojte tento router a pokračujte s dalším.", None))
        self.finalToScan.setText(_translate("Installer", "Další router", None))
        self.label_17.setText(_translate("Installer", "<h1>Chyba</h1>", None))
        self.tmpErrMsg.setText(_translate("Installer", "Zkontrolujte připojení kabelů.", None))
        self.chckToStepX.setText(_translate("Installer", "Zkusit znovu", None))
        self.label_13.setText(_translate("Installer", "<h1>Chyba</h1>", None))
        self.label_14.setText(_translate("Installer", "Vezměte router, odpojte kabely, otevřte okno a hoďte router z okna. Pak pokračujte dalším.", None))
        self.errToScan.setText(_translate("Installer", "Další router", None))
        self.label.setText(_translate("Installer", "Turris firmware flasher", None))

