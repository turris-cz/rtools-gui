# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'installer.ui'
#
# Created: Thu Dec 19 09:55:04 2013
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
        self.label_5.setTextFormat(QtCore.Qt.RichText)
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
        self.stepReset = QtGui.QWidget()
        self.stepReset.setObjectName(_fromUtf8("stepReset"))
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.stepReset)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.label_19 = QtGui.QLabel(self.stepReset)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.verticalLayout_13.addWidget(self.label_19)
        self.label_24 = QtGui.QLabel(self.stepReset)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_24.sizePolicy().hasHeightForWidth())
        self.label_24.setSizePolicy(sizePolicy)
        self.label_24.setWordWrap(True)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.verticalLayout_13.addWidget(self.label_24)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.resetToThree = QtGui.QPushButton(self.stepReset)
        self.resetToThree.setObjectName(_fromUtf8("resetToThree"))
        self.horizontalLayout_9.addWidget(self.resetToThree)
        self.verticalLayout_13.addLayout(self.horizontalLayout_9)
        self.stackedWidget.addWidget(self.stepReset)
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
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem3)
        self.finalToTest = QtGui.QPushButton(self.stepFinal)
        self.finalToTest.setObjectName(_fromUtf8("finalToTest"))
        self.horizontalLayout_7.addWidget(self.finalToTest)
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
        self.tmpErrMsg.setText(_fromUtf8(""))
        self.tmpErrMsg.setWordWrap(True)
        self.tmpErrMsg.setObjectName(_fromUtf8("tmpErrMsg"))
        self.verticalLayout_9.addWidget(self.tmpErrMsg)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
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
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.errToScan = QtGui.QPushButton(self.finalErrorPage)
        self.errToScan.setObjectName(_fromUtf8("errToScan"))
        self.horizontalLayout_6.addWidget(self.errToScan)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.stackedWidget.addWidget(self.finalErrorPage)
        self.testingInfo = QtGui.QWidget()
        self.testingInfo.setObjectName(_fromUtf8("testingInfo"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.testingInfo)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.label_18 = QtGui.QLabel(self.testingInfo)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.verticalLayout_10.addWidget(self.label_18)
        self.testResultLabel = QtGui.QLabel(self.testingInfo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.testResultLabel.sizePolicy().hasHeightForWidth())
        self.testResultLabel.setSizePolicy(sizePolicy)
        self.testResultLabel.setText(_fromUtf8(""))
        self.testResultLabel.setTextFormat(QtCore.Qt.RichText)
        self.testResultLabel.setWordWrap(True)
        self.testResultLabel.setObjectName(_fromUtf8("testResultLabel"))
        self.verticalLayout_10.addWidget(self.testResultLabel)
        self.nextTestDesc = QtGui.QLabel(self.testingInfo)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.nextTestDesc.setFont(font)
        self.nextTestDesc.setText(_fromUtf8(""))
        self.nextTestDesc.setTextFormat(QtCore.Qt.PlainText)
        self.nextTestDesc.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nextTestDesc.setObjectName(_fromUtf8("nextTestDesc"))
        self.verticalLayout_10.addWidget(self.nextTestDesc)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem6)
        self.prepTestToRunTest = QtGui.QPushButton(self.testingInfo)
        self.prepTestToRunTest.setObjectName(_fromUtf8("prepTestToRunTest"))
        self.horizontalLayout_5.addWidget(self.prepTestToRunTest)
        self.verticalLayout_10.addLayout(self.horizontalLayout_5)
        self.stackedWidget.addWidget(self.testingInfo)
        self.testingProgress = QtGui.QWidget()
        self.testingProgress.setObjectName(_fromUtf8("testingProgress"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.testingProgress)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.label_20 = QtGui.QLabel(self.testingProgress)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.verticalLayout_11.addWidget(self.label_20)
        self.runningTestDesc = QtGui.QLabel(self.testingProgress)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.runningTestDesc.sizePolicy().hasHeightForWidth())
        self.runningTestDesc.setSizePolicy(sizePolicy)
        self.runningTestDesc.setText(_fromUtf8(""))
        self.runningTestDesc.setTextFormat(QtCore.Qt.PlainText)
        self.runningTestDesc.setWordWrap(True)
        self.runningTestDesc.setObjectName(_fromUtf8("runningTestDesc"))
        self.verticalLayout_11.addWidget(self.runningTestDesc)
        self.progressBar_4 = QtGui.QProgressBar(self.testingProgress)
        self.progressBar_4.setMinimum(0)
        self.progressBar_4.setMaximum(0)
        self.progressBar_4.setProperty("value", -1)
        self.progressBar_4.setObjectName(_fromUtf8("progressBar_4"))
        self.verticalLayout_11.addWidget(self.progressBar_4)
        self.stackedWidget.addWidget(self.testingProgress)
        self.theEnd = QtGui.QWidget()
        self.theEnd.setObjectName(_fromUtf8("theEnd"))
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.theEnd)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.label_22 = QtGui.QLabel(self.theEnd)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.verticalLayout_12.addWidget(self.label_22)
        self.label_23 = QtGui.QLabel(self.theEnd)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_23.sizePolicy().hasHeightForWidth())
        self.label_23.setSizePolicy(sizePolicy)
        self.label_23.setWordWrap(True)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.verticalLayout_12.addWidget(self.label_23)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem7)
        self.endToScan = QtGui.QPushButton(self.theEnd)
        self.endToScan.setObjectName(_fromUtf8("endToScan"))
        self.horizontalLayout_8.addWidget(self.endToScan)
        self.verticalLayout_12.addLayout(self.horizontalLayout_8)
        self.stackedWidget.addWidget(self.theEnd)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.label = QtGui.QLabel(Installer)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(Installer)
        QtCore.QMetaObject.connectSlotsByName(Installer)

    def retranslateUi(self, Installer):
        Installer.setWindowTitle(_translate("Installer", "Instalátor", None))
        self.label_2.setText(_translate("Installer", "<html><head/><body><p><span style=\" font-size:xx-large; font-weight:600;\">Začínáme</span></p></body></html>", None))
        self.label_8.setText(_translate("Installer", "<ul>\n"
"<li style=\"margin-bottom: 10px;\">Zkontrolujte pracoviště pro programování a testování routeru TURRIS podle přiložené dokumentace.\n"
"</li>\n"
"<li style=\"margin-bottom: 10px;\">Zejména ověřte všechny datové kabely 1 až 7, napájecí kabely , funkčnost TURRIS PROGRAMMERu\n"
"</li>\n"
"<li style=\"margin-bottom: 10px;\">Vložte paměťový modul DDR3 SODIMM do slotu</li>\n"
"<li style=\"margin-bottom: 10px;\">Nastavte DIP SWITCHe SW1 a SW2 dle návodu</li>\n"
"<li style=\"margin-bottom: 10px;\">Vložte baterii do patice BT1</li>\n"
"<li style=\"margin-bottom: 10px;\">Přilepte chladiče na procesor a LAN switch</li>\n"
"</ul>", None))
        self.startToScan.setText(_translate("Installer", "Pokračovat", None))
        self.label_3.setText(_translate("Installer", "<h1>Scan</h1>", None))
        self.label_5.setText(_translate("Installer", "<html><head/><body><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:10px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Nalepte na konektor CN3 malý štítek a odstřihněte z kotouče velké štítky, které přiložte k programované desce. </li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Sejměte čárový kód nalepený na LAN konektoru desky routeru TURRIS. </li></ul></body></html>", None))
        self.label_4.setText(_translate("Installer", "Čárový kód", None))
        self.scanToOne.setText(_translate("Installer", "Spustit programování", None))
        self.label_15.setText(_translate("Installer", "<h1>I2C Programování</h1>", None))
        self.label_16.setText(_translate("Installer", "V tomto kroku se programují přes kabel 1 a I2C sběrnici následující zařízení: Zdroj, Cryptochip, RTC, Teploměr.", None))
        self.label_6.setText(_translate("Installer", "<h1>CPLD Programování</h1>", None))
        self.label_7.setText(_translate("Installer", "V tomto kroku probíhá programování CPLD obvodu pomocí kabelu 2.", None))
        self.label_19.setText(_translate("Installer", "<h1>Restart</h1>", None))
        self.label_24.setText(_translate("Installer", "Odpojte a zapojte kabel napájení 7,5V. Zkontrolujte vložení baterie.", None))
        self.resetToThree.setText(_translate("Installer", "Pokračovat", None))
        self.label_9.setText(_translate("Installer", "<h1>FLASH Programování</h1>", None))
        self.label_10.setText(_translate("Installer", "V tomto kroku probíhá programování NOR Flash paměti procesoru pomocí kabelu 3. Prosím vyčkejte přibližně 5 minut na dokončení.", None))
        self.label_11.setText(_translate("Installer", "<h1>Naprogramováno</h1>", None))
        self.label_12.setText(_translate("Installer", "Operace programování desky routeru TURRIS skončila úspěšně. Ověřte připojení všech kabelů nezbytných k testování funkčnosti.", None))
        self.finalToTest.setText(_translate("Installer", "Testovat router", None))
        self.label_17.setText(_translate("Installer", "<h1>Chyba</h1>", None))
        self.chckToStepX.setText(_translate("Installer", "Zkusit znovu", None))
        self.label_13.setText(_translate("Installer", "<h1>Chyba</h1>", None))
        self.label_14.setText(_translate("Installer", "Během programování se vyskytla chyba. Odložte desku routeru TURRIS pro další analýzu.", None))
        self.errToScan.setText(_translate("Installer", "Další router", None))
        self.label_18.setText(_translate("Installer", "<h1>Testování</h1>", None))
        self.prepTestToRunTest.setText(_translate("Installer", "Spustit test", None))
        self.label_20.setText(_translate("Installer", "<h1>Testování</h1>", None))
        self.label_22.setText(_translate("Installer", "<h1>Konec</h1>", None))
        self.label_23.setText(_translate("Installer", "Router byl naflashován a zkontrolován.", None))
        self.endToScan.setText(_translate("Installer", "Další router", None))
        self.label.setText(_translate("Installer", "Turris firmware flasher", None))

