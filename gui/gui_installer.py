# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'installer.ui'
#
# Created: Mon Jan  6 10:58:02 2014
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
        Installer.resize(600, 500)
        self.centralwidget = QtGui.QWidget(Installer)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.stackedWidget = QtGui.QStackedWidget(self.centralwidget)
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
        self.flashFinished = QtGui.QWidget()
        self.flashFinished.setObjectName(_fromUtf8("flashFinished"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.flashFinished)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_11 = QtGui.QLabel(self.flashFinished)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_7.addWidget(self.label_11)
        self.label_12 = QtGui.QLabel(self.flashFinished)
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
        self.finalToReset = QtGui.QPushButton(self.flashFinished)
        self.finalToReset.setObjectName(_fromUtf8("finalToReset"))
        self.horizontalLayout_7.addWidget(self.finalToReset)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.stackedWidget.addWidget(self.flashFinished)
        self.stepAfterReset = QtGui.QWidget()
        self.stepAfterReset.setObjectName(_fromUtf8("stepAfterReset"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.stepAfterReset)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.label_21 = QtGui.QLabel(self.stepAfterReset)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.verticalLayout_14.addWidget(self.label_21)
        self.label_25 = QtGui.QLabel(self.stepAfterReset)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_25.sizePolicy().hasHeightForWidth())
        self.label_25.setSizePolicy(sizePolicy)
        self.label_25.setWordWrap(True)
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.verticalLayout_14.addWidget(self.label_25)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem4)
        self.resetToTests = QtGui.QPushButton(self.stepAfterReset)
        self.resetToTests.setObjectName(_fromUtf8("resetToTests"))
        self.horizontalLayout_10.addWidget(self.resetToTests)
        self.verticalLayout_14.addLayout(self.horizontalLayout_10)
        self.stackedWidget.addWidget(self.stepAfterReset)
        self.beforeTests = QtGui.QWidget()
        self.beforeTests.setObjectName(_fromUtf8("beforeTests"))
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.beforeTests)
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.label_26 = QtGui.QLabel(self.beforeTests)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.verticalLayout_15.addWidget(self.label_26)
        self.label_27 = QtGui.QLabel(self.beforeTests)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_27.sizePolicy().hasHeightForWidth())
        self.label_27.setSizePolicy(sizePolicy)
        self.label_27.setWordWrap(True)
        self.label_27.setObjectName(_fromUtf8("label_27"))
        self.verticalLayout_15.addWidget(self.label_27)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem5)
        self.prepareToFirstTest = QtGui.QPushButton(self.beforeTests)
        self.prepareToFirstTest.setObjectName(_fromUtf8("prepareToFirstTest"))
        self.horizontalLayout_11.addWidget(self.prepareToFirstTest)
        self.verticalLayout_15.addLayout(self.horizontalLayout_11)
        self.stackedWidget.addWidget(self.beforeTests)
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
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem6)
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
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem7)
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
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem8)
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
        self.finalSummary = QtGui.QLabel(self.theEnd)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.finalSummary.sizePolicy().hasHeightForWidth())
        self.finalSummary.setSizePolicy(sizePolicy)
        self.finalSummary.setTextFormat(QtCore.Qt.RichText)
        self.finalSummary.setWordWrap(True)
        self.finalSummary.setObjectName(_fromUtf8("finalSummary"))
        self.verticalLayout_12.addWidget(self.finalSummary)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem9)
        self.endToScan = QtGui.QPushButton(self.theEnd)
        self.endToScan.setObjectName(_fromUtf8("endToScan"))
        self.horizontalLayout_8.addWidget(self.endToScan)
        self.verticalLayout_12.addLayout(self.horizontalLayout_8)
        self.stackedWidget.addWidget(self.theEnd)
        self.accessories = QtGui.QWidget()
        self.accessories.setObjectName(_fromUtf8("accessories"))
        self.verticalLayout_16 = QtGui.QVBoxLayout(self.accessories)
        self.verticalLayout_16.setObjectName(_fromUtf8("verticalLayout_16"))
        self.label_28 = QtGui.QLabel(self.accessories)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.verticalLayout_16.addWidget(self.label_28)
        spacerItem10 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_16.addItem(spacerItem10)
        self.toAccessoriesTests = QtGui.QCommandLinkButton(self.accessories)
        self.toAccessoriesTests.setObjectName(_fromUtf8("toAccessoriesTests"))
        self.verticalLayout_16.addWidget(self.toAccessoriesTests)
        self.toAccessoriesCPLDErase = QtGui.QCommandLinkButton(self.accessories)
        self.toAccessoriesCPLDErase.setObjectName(_fromUtf8("toAccessoriesCPLDErase"))
        self.verticalLayout_16.addWidget(self.toAccessoriesCPLDErase)
        spacerItem11 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_16.addItem(spacerItem11)
        self.stackedWidget.addWidget(self.accessories)
        self.onlyTests = QtGui.QWidget()
        self.onlyTests.setObjectName(_fromUtf8("onlyTests"))
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.onlyTests)
        self.verticalLayout_17.setObjectName(_fromUtf8("verticalLayout_17"))
        self.label_29 = QtGui.QLabel(self.onlyTests)
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.verticalLayout_17.addWidget(self.label_29)
        self.label_30 = QtGui.QLabel(self.onlyTests)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)
        self.label_30.setWordWrap(True)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.verticalLayout_17.addWidget(self.label_30)
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.label_31 = QtGui.QLabel(self.onlyTests)
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.horizontalLayout_12.addWidget(self.label_31)
        self.barcodeOnlyTests = QtGui.QLineEdit(self.onlyTests)
        self.barcodeOnlyTests.setObjectName(_fromUtf8("barcodeOnlyTests"))
        self.horizontalLayout_12.addWidget(self.barcodeOnlyTests)
        self.verticalLayout_17.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        spacerItem12 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem12)
        self.toOnlyTests = QtGui.QPushButton(self.onlyTests)
        self.toOnlyTests.setObjectName(_fromUtf8("toOnlyTests"))
        self.horizontalLayout_13.addWidget(self.toOnlyTests)
        self.verticalLayout_17.addLayout(self.horizontalLayout_13)
        self.stackedWidget.addWidget(self.onlyTests)
        self.cpldErase = QtGui.QWidget()
        self.cpldErase.setObjectName(_fromUtf8("cpldErase"))
        self.verticalLayout_18 = QtGui.QVBoxLayout(self.cpldErase)
        self.verticalLayout_18.setObjectName(_fromUtf8("verticalLayout_18"))
        self.label = QtGui.QLabel(self.cpldErase)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_18.addWidget(self.label)
        self.cpldDeleteStack = QtGui.QStackedWidget(self.cpldErase)
        self.cpldDeleteStack.setObjectName(_fromUtf8("cpldDeleteStack"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.verticalLayout_19 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_19.setObjectName(_fromUtf8("verticalLayout_19"))
        self.label_33 = QtGui.QLabel(self.page)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label_33.sizePolicy().hasHeightForWidth())
        self.label_33.setSizePolicy(sizePolicy)
        self.label_33.setWordWrap(True)
        self.label_33.setObjectName(_fromUtf8("label_33"))
        self.verticalLayout_19.addWidget(self.label_33)
        self.horizontalLayout_16 = QtGui.QHBoxLayout()
        self.horizontalLayout_16.setObjectName(_fromUtf8("horizontalLayout_16"))
        spacerItem13 = QtGui.QSpacerItem(348, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem13)
        self.startEraseCpld = QtGui.QPushButton(self.page)
        self.startEraseCpld.setObjectName(_fromUtf8("startEraseCpld"))
        self.horizontalLayout_16.addWidget(self.startEraseCpld)
        self.verticalLayout_19.addLayout(self.horizontalLayout_16)
        self.cpldDeleteStack.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.verticalLayout_20 = QtGui.QVBoxLayout(self.page_2)
        self.verticalLayout_20.setObjectName(_fromUtf8("verticalLayout_20"))
        self.label_32 = QtGui.QLabel(self.page_2)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.verticalLayout_20.addWidget(self.label_32)
        self.progressBar_5 = QtGui.QProgressBar(self.page_2)
        self.progressBar_5.setMaximum(0)
        self.progressBar_5.setProperty("value", 0)
        self.progressBar_5.setObjectName(_fromUtf8("progressBar_5"))
        self.verticalLayout_20.addWidget(self.progressBar_5)
        self.cpldDeleteStack.addWidget(self.page_2)
        self.verticalLayout_18.addWidget(self.cpldDeleteStack)
        self.stackedWidget.addWidget(self.cpldErase)
        self.verticalLayout.addWidget(self.stackedWidget)
        Installer.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Installer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 24))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuAkce = QtGui.QMenu(self.menubar)
        self.menuAkce.setObjectName(_fromUtf8("menuAkce"))
        self.menuN_stroje = QtGui.QMenu(self.menubar)
        self.menuN_stroje.setObjectName(_fromUtf8("menuN_stroje"))
        Installer.setMenuBar(self.menubar)
        self.actionKonec = QtGui.QAction(Installer)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("application-exit"))
        self.actionKonec.setIcon(icon)
        self.actionKonec.setObjectName(_fromUtf8("actionKonec"))
        self.actionDalsifunkce = QtGui.QAction(Installer)
        self.actionDalsifunkce.setObjectName(_fromUtf8("actionDalsifunkce"))
        self.actionTestovani = QtGui.QAction(Installer)
        self.actionTestovani.setObjectName(_fromUtf8("actionTestovani"))
        self.actionSmazaniCPLD = QtGui.QAction(Installer)
        self.actionSmazaniCPLD.setObjectName(_fromUtf8("actionSmazaniCPLD"))
        self.menuAkce.addAction(self.actionKonec)
        self.menuN_stroje.addAction(self.actionDalsifunkce)
        self.menuN_stroje.addSeparator()
        self.menuN_stroje.addAction(self.actionTestovani)
        self.menuN_stroje.addAction(self.actionSmazaniCPLD)
        self.menubar.addAction(self.menuAkce.menuAction())
        self.menubar.addAction(self.menuN_stroje.menuAction())

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
        self.label_5.setText(_translate("Installer", "<html><head/><body><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:10px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Nalepte na konektor CN3 malý štítek a odstřihněte z kotouče velké štítky, které přiložte k programované desce. </li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; \n"
"margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Sejměte čárový kód nalepený na LAN konektoru desky routeru TURRIS. </li></ul></body></html>", None))
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
        self.label_11.setText(_translate("Installer", "<h1>Rozbalení OS do NAND</h1>", None))
        self.label_12.setText(_translate("Installer", "Podržte minimálně 6 sekund tlačítko RESET (červené). LED dioda POWER bude blikat v intervalech 1 sekunda. Po 6 sekundách přestane blikat a tlačítko RESET můžete uvolnit.", None))
        self.finalToReset.setText(_translate("Installer", "RESET po 6s stisknutí uvolněno", None))
        self.label_21.setText(_translate("Installer", "<h1>Rozbalení OS do NAND</h1>", None))
        self.label_25.setText(_translate("Installer", "<ul>\n"
"<li style=\"margin-bottom: 10px;\">Probíhá rozbalení OS do NAND. Vyčkejte přibližně 1 minutu.</li>\n"
"<li style=\"margin-bottom: 10px;\">Po rozbalení OS do NAND se router sám zresetuje což bude indikováno zablikáním předních LED diod.</li></ul>", None))
        self.resetToTests.setText(_translate("Installer", "Router se zresetoval", None))
        self.label_26.setText(_translate("Installer", "<h1>Reset po rozbalení OS</h1>", None))
        self.label_27.setText(_translate("Installer", "<ul>\n"
"<li style=\"margin-bottom: 10px;\">Router bude potřeba znovu zresetovat. Odpojte kabel č.5 od routeru.</li>\n"
"<li style=\"margin-bottom: 10px;\">Stiskněte krátce (&lt;5s) tlačítko RESET.</li>\n"
"<li style=\"margin-bottom: 10px;\">Zapojte kabel č.5 do routeru.</li>\n"
"</ul>", None))
        self.prepareToFirstTest.setText(_translate("Installer", "Projít na testy", None))
        self.label_17.setText(_translate("Installer", "<h1>Chyba</h1>", None))
        self.chckToStepX.setText(_translate("Installer", "Zkusit znovu", None))
        self.label_13.setText(_translate("Installer", "<h1>Chyba</h1>", None))
        self.label_14.setText(_translate("Installer", "Během programování se vyskytla chyba. Odložte desku routeru TURRIS pro další analýzu.", None))
        self.errToScan.setText(_translate("Installer", "Další router", None))
        self.label_18.setText(_translate("Installer", "<h1>Testování</h1>", None))
        self.prepTestToRunTest.setText(_translate("Installer", "Spustit test", None))
        self.label_20.setText(_translate("Installer", "<h1>Testování</h1>", None))
        self.label_22.setText(_translate("Installer", "<h1>Konec</h1>", None))
        self.finalSummary.setText(_translate("Installer", "<html><head/><body><p><br/></p></body></html>", None))
        self.endToScan.setText(_translate("Installer", "Další router", None))
        self.label_28.setText(_translate("Installer", "<h1>Další funkce</h1>", None))
        self.toAccessoriesTests.setText(_translate("Installer", "Znovu vykonat testy na již naflashovaném routeru", None))
        self.toAccessoriesCPLDErase.setText(_translate("Installer", "Vymazat CPLD", None))
        self.label_29.setText(_translate("Installer", "<h1>Testování</h1>", None))
        self.label_30.setText(_translate("Installer", "Sejměte čárový kód nalepený na LAN konektoru desky routeru TURRIS nebo na spodní straně krabice (tyto kódy jsou stejné).", None))
        self.label_31.setText(_translate("Installer", "Čárový kód", None))
        self.toOnlyTests.setText(_translate("Installer", "Otestovat tento router", None))
        self.label.setText(_translate("Installer", "<h1>Smazání CPLD obvodu</h1>", None))
        self.label_33.setText(_translate("Installer", "Před provedením této operace zkontrolujte připojení kabelu 2 a napájecího adaptéru 7,5V.", None))
        self.startEraseCpld.setText(_translate("Installer", "Smazat CPLD", None))
        self.label_32.setText(_translate("Installer", "Probíhá mazání obvodu CPLD.", None))
        self.menuAkce.setTitle(_translate("Installer", "&Soubor", None))
        self.menuN_stroje.setTitle(_translate("Installer", "&Nástroje", None))
        self.actionKonec.setText(_translate("Installer", "Konec", None))
        self.actionDalsifunkce.setText(_translate("Installer", "Další funkce", None))
        self.actionTestovani.setText(_translate("Installer", "Testování", None))
        self.actionSmazaniCPLD.setText(_translate("Installer", "Smazání CPLD obvodu", None))

