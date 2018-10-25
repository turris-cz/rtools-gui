# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/programmer.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Programmer(object):
    def setupUi(self, Programmer):
        Programmer.setObjectName("Programmer")
        Programmer.resize(656, 558)
        Programmer.setFrameShape(QtWidgets.QFrame.Box)
        Programmer.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout = QtWidgets.QVBoxLayout(Programmer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.indexLabel = QtWidgets.QLabel(Programmer)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.indexLabel.setFont(font)
        self.indexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.indexLabel.setObjectName("indexLabel")
        self.verticalLayout.addWidget(self.indexLabel)
        self.contentWidget = QtWidgets.QStackedWidget(Programmer)
        self.contentWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.contentWidget.setObjectName("contentWidget")
        self.pageIntro = QtWidgets.QWidget()
        self.pageIntro.setObjectName("pageIntro")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.pageIntro)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.pageIntro)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(300, 300))
        self.label.setMaximumSize(QtCore.QSize(300, 300))
        self.label.setBaseSize(QtCore.QSize(0, 0))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/img/favicon-big.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.introWidget = QtWidgets.QStackedWidget(self.pageIntro)
        self.introWidget.setObjectName("introWidget")
        self.pageIntroConnect = QtWidgets.QWidget()
        self.pageIntroConnect.setObjectName("pageIntroConnect")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pageIntroConnect)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.pageIntroConnect)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.pushButton_2 = QtWidgets.QPushButton(self.pageIntroConnect)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(16)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.introWidget.addWidget(self.pageIntroConnect)
        self.pageIntroReady = QtWidgets.QWidget()
        self.pageIntroReady.setObjectName("pageIntroReady")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.pageIntroReady)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.introMessageLabel = QtWidgets.QLabel(self.pageIntroReady)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.introMessageLabel.setFont(font)
        self.introMessageLabel.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.introMessageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.introMessageLabel.setObjectName("introMessageLabel")
        self.verticalLayout_7.addWidget(self.introMessageLabel)
        self.introErrorLabel = QtWidgets.QLabel(self.pageIntroReady)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.introErrorLabel.setFont(font)
        self.introErrorLabel.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.introErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.introErrorLabel.setObjectName("introErrorLabel")
        self.verticalLayout_7.addWidget(self.introErrorLabel)
        self.introWidget.addWidget(self.pageIntroReady)
        self.pageIntroSerial = QtWidgets.QWidget()
        self.pageIntroSerial.setObjectName("pageIntroSerial")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.pageIntroSerial)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.scanBoardLabel = QtWidgets.QLabel(self.pageIntroSerial)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.scanBoardLabel.setFont(font)
        self.scanBoardLabel.setObjectName("scanBoardLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.scanBoardLabel)
        self.barcodeLineEdit = QtWidgets.QLineEdit(self.pageIntroSerial)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.barcodeLineEdit.setFont(font)
        self.barcodeLineEdit.setObjectName("barcodeLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.barcodeLineEdit)
        self.verticalLayout_4.addLayout(self.formLayout)
        self.introWidget.addWidget(self.pageIntroSerial)
        self.verticalLayout_3.addWidget(self.introWidget)
        self.contentWidget.addWidget(self.pageIntro)
        self.pageWork = QtWidgets.QWidget()
        self.pageWork.setObjectName("pageWork")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.pageWork)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.typeLabel = QtWidgets.QLabel(self.pageWork)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.typeLabel.setFont(font)
        self.typeLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.typeLabel.setObjectName("typeLabel")
        self.horizontalLayout_2.addWidget(self.typeLabel)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.serialNumberLabel = QtWidgets.QLabel(self.pageWork)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.serialNumberLabel.setFont(font)
        self.serialNumberLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.serialNumberLabel.setObjectName("serialNumberLabel")
        self.horizontalLayout_2.addWidget(self.serialNumberLabel)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.programmerTabWidget = QtWidgets.QTabWidget(self.pageWork)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.programmerTabWidget.sizePolicy().hasHeightForWidth())
        self.programmerTabWidget.setSizePolicy(sizePolicy)
        self.programmerTabWidget.setTabPosition(QtWidgets.QTabWidget.East)
        self.programmerTabWidget.setObjectName("programmerTabWidget")
        self.tabProgress = QtWidgets.QWidget()
        self.tabProgress.setObjectName("tabProgress")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tabProgress)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.scrollArea = QtWidgets.QScrollArea(self.tabProgress)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.ProgressContent = QtWidgets.QWidget()
        self.ProgressContent.setGeometry(QtCore.QRect(0, 0, 602, 392))
        self.ProgressContent.setObjectName("ProgressContent")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.ProgressContent)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        spacerItem5 = QtWidgets.QSpacerItem(20, 371, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem5)
        self.scrollArea.setWidget(self.ProgressContent)
        self.verticalLayout_6.addWidget(self.scrollArea)
        self.programmerTabWidget.addTab(self.tabProgress, "")
        self.tabInfo = QtWidgets.QWidget()
        self.tabInfo.setObjectName("tabInfo")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.tabInfo)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tabInfo)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 602, 392))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_11.addWidget(self.scrollArea_2)
        self.programmerTabWidget.addTab(self.tabInfo, "")
        self.tabLog = QtWidgets.QWidget()
        self.tabLog.setObjectName("tabLog")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.tabLog)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.scrollArea_3 = QtWidgets.QScrollArea(self.tabLog)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 602, 392))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout_12.addWidget(self.scrollArea_3)
        self.programmerTabWidget.addTab(self.tabLog, "")
        self.verticalLayout_5.addWidget(self.programmerTabWidget)
        self.progressWidget = QtWidgets.QStackedWidget(self.pageWork)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressWidget.sizePolicy().hasHeightForWidth())
        self.progressWidget.setSizePolicy(sizePolicy)
        self.progressWidget.setObjectName("progressWidget")
        self.progressProgress = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressProgress.sizePolicy().hasHeightForWidth())
        self.progressProgress.setSizePolicy(sizePolicy)
        self.progressProgress.setObjectName("progressProgress")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.progressProgress)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.currentProgress = QtWidgets.QProgressBar(self.progressProgress)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentProgress.sizePolicy().hasHeightForWidth())
        self.currentProgress.setSizePolicy(sizePolicy)
        self.currentProgress.setMaximum(100)
        self.currentProgress.setProperty("value", 0)
        self.currentProgress.setObjectName("currentProgress")
        self.verticalLayout_9.addWidget(self.currentProgress)
        self.totalProgress = QtWidgets.QProgressBar(self.progressProgress)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.totalProgress.sizePolicy().hasHeightForWidth())
        self.totalProgress.setSizePolicy(sizePolicy)
        self.totalProgress.setMaximum(0)
        self.totalProgress.setProperty("value", 0)
        self.totalProgress.setObjectName("totalProgress")
        self.verticalLayout_9.addWidget(self.totalProgress)
        self.progressWidget.addWidget(self.progressProgress)
        self.progressError = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressError.sizePolicy().hasHeightForWidth())
        self.progressError.setSizePolicy(sizePolicy)
        self.progressError.setObjectName("progressError")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.progressError)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.progressErrorLabel = QtWidgets.QLabel(self.progressError)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressErrorLabel.sizePolicy().hasHeightForWidth())
        self.progressErrorLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(20)
        self.progressErrorLabel.setFont(font)
        self.progressErrorLabel.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.progressErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.progressErrorLabel.setObjectName("progressErrorLabel")
        self.verticalLayout_10.addWidget(self.progressErrorLabel)
        self.progressWidget.addWidget(self.progressError)
        self.verticalLayout_5.addWidget(self.progressWidget)
        self.contentWidget.addWidget(self.pageWork)
        self.verticalLayout.addWidget(self.contentWidget)

        self.retranslateUi(Programmer)
        self.contentWidget.setCurrentIndex(0)
        self.introWidget.setCurrentIndex(0)
        self.programmerTabWidget.setCurrentIndex(0)
        self.progressWidget.setCurrentIndex(0)
        self.pushButton_2.clicked.connect(Programmer.connectProgrammer)
        self.barcodeLineEdit.editingFinished.connect(Programmer.barcodeAbandon)
        self.barcodeLineEdit.returnPressed.connect(Programmer.barcodeScanEnter)
        QtCore.QMetaObject.connectSlotsByName(Programmer)

    def retranslateUi(self, Programmer):
        _translate = QtCore.QCoreApplication.translate
        Programmer.setWindowTitle(_translate("Programmer", "Form"))
        self.indexLabel.setText(_translate("Programmer", "#PROGRAMMER NUMBER#"))
        self.label_2.setText(_translate("Programmer", "PROGRAMÁTOR ODPOJEN"))
        self.pushButton_2.setText(_translate("Programmer", "Pokusit se znovu o spojení"))
        self.introMessageLabel.setText(_translate("Programmer", "Programátor připraven"))
        self.introErrorLabel.setText(_translate("Programmer", "#ERROR#"))
        self.scanBoardLabel.setText(_translate("Programmer", "Naskenujte kód desky:"))
        self.typeLabel.setText(_translate("Programmer", "#TYPE#"))
        self.serialNumberLabel.setText(_translate("Programmer", "#SERIAL NUMBER#"))
        self.programmerTabWidget.setTabText(self.programmerTabWidget.indexOf(self.tabProgress), _translate("Programmer", "Průběh"))
        self.programmerTabWidget.setTabText(self.programmerTabWidget.indexOf(self.tabInfo), _translate("Programmer", "Informace"))
        self.programmerTabWidget.setTabText(self.programmerTabWidget.indexOf(self.tabLog), _translate("Programmer", "Log"))
        self.currentProgress.setFormat(_translate("Programmer", "%p%"))
        self.totalProgress.setFormat(_translate("Programmer", "%v/%m"))
        self.progressErrorLabel.setText(_translate("Programmer", "#ERROR#"))

from qrc import icons
