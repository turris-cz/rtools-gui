# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(750, 900)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/favicon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkNeededLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.checkNeededLabel.setFont(font)
        self.checkNeededLabel.setStyleSheet("background-color: orangered;")
        self.checkNeededLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.checkNeededLabel.setObjectName("checkNeededLabel")
        self.verticalLayout.addWidget(self.checkNeededLabel)
        self.workstationTestLabel = QtWidgets.QLabel(self.centralwidget)
        self.workstationTestLabel.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.workstationTestLabel.setFont(font)
        self.workstationTestLabel.setAutoFillBackground(False)
        self.workstationTestLabel.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.workstationTestLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.workstationTestLabel.setObjectName("workstationTestLabel")
        self.verticalLayout.addWidget(self.workstationTestLabel)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_9.addWidget(self.label_3)
        self.ramLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.ramLabel.setFont(font)
        self.ramLabel.setObjectName("ramLabel")
        self.horizontalLayout_9.addWidget(self.ramLabel)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_9.addWidget(self.label_7)
        self.regionLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.regionLabel.setFont(font)
        self.regionLabel.setObjectName("regionLabel")
        self.horizontalLayout_9.addWidget(self.regionLabel)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.lastResultsLayout = QtWidgets.QHBoxLayout()
        self.lastResultsLayout.setObjectName("lastResultsLayout")
        self.horizontalLayout_8.addLayout(self.lastResultsLayout)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.verticalLayout_6.addLayout(self.horizontalLayout_8)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_6.addWidget(self.line)
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.barcodePage = QtWidgets.QWidget()
        self.barcodePage.setObjectName("barcodePage")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.barcodePage)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.titleLabel = QtWidgets.QLabel(self.barcodePage)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout_2.addWidget(self.titleLabel)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.barcodePage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(300, 300))
        self.label.setMaximumSize(QtCore.QSize(300, 300))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/img/favicon-big.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.errorLabel = QtWidgets.QLabel(self.barcodePage)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.errorLabel.setFont(font)
        self.errorLabel.setStyleSheet("#errorLabel {\n"
"    color: red;\n"
"}")
        self.errorLabel.setText("")
        self.errorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.errorLabel.setObjectName("errorLabel")
        self.verticalLayout_2.addWidget(self.errorLabel)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.barcodePage)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.barcodeLineEdit = QtWidgets.QLineEdit(self.barcodePage)
        self.barcodeLineEdit.setObjectName("barcodeLineEdit")
        self.horizontalLayout_3.addWidget(self.barcodeLineEdit)
        self.scanButton = QtWidgets.QPushButton(self.barcodePage)
        self.scanButton.setText("")
        self.scanButton.setObjectName("scanButton")
        self.horizontalLayout_3.addWidget(self.scanButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.stackedWidget.addWidget(self.barcodePage)
        self.workPage = QtWidgets.QWidget()
        self.workPage.setObjectName("workPage")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.workPage)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.backButton = QtWidgets.QPushButton(self.workPage)
        self.backButton.setText("")
        self.backButton.setObjectName("backButton")
        self.horizontalLayout_2.addWidget(self.backButton)
        self.serialNumberLabel = QtWidgets.QLabel(self.workPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serialNumberLabel.sizePolicy().hasHeightForWidth())
        self.serialNumberLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.serialNumberLabel.setFont(font)
        self.serialNumberLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.serialNumberLabel.setObjectName("serialNumberLabel")
        self.horizontalLayout_2.addWidget(self.serialNumberLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.stepFrame = QtWidgets.QFrame(self.workPage)
        self.stepFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.stepFrame.setObjectName("stepFrame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.stepFrame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.stepFrame)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        self.scrollArea = QtWidgets.QScrollArea(self.stepFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.stepsLayoutWidget = QtWidgets.QWidget()
        self.stepsLayoutWidget.setGeometry(QtCore.QRect(0, 0, 16, 16))
        self.stepsLayoutWidget.setObjectName("stepsLayoutWidget")
        self.stepsLayout = QtWidgets.QGridLayout(self.stepsLayoutWidget)
        self.stepsLayout.setContentsMargins(0, 0, 0, 0)
        self.stepsLayout.setSpacing(6)
        self.stepsLayout.setObjectName("stepsLayout")
        self.scrollArea.setWidget(self.stepsLayoutWidget)
        self.verticalLayout_5.addWidget(self.scrollArea)
        self.horizontalLayout_4.addWidget(self.stepFrame)
        self.testFrame = QtWidgets.QFrame(self.workPage)
        self.testFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.testFrame.setObjectName("testFrame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.testFrame)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.testFrame)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_4.addWidget(self.label_5)
        self.scrollArea_2 = QtWidgets.QScrollArea(self.testFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.scrollArea_2.sizePolicy().hasHeightForWidth())
        self.scrollArea_2.setSizePolicy(sizePolicy)
        self.scrollArea_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.testsLayoutWidget = QtWidgets.QWidget()
        self.testsLayoutWidget.setGeometry(QtCore.QRect(0, 0, 16, 16))
        self.testsLayoutWidget.setObjectName("testsLayoutWidget")
        self.testsLayout = QtWidgets.QGridLayout(self.testsLayoutWidget)
        self.testsLayout.setContentsMargins(0, 0, 0, 0)
        self.testsLayout.setSpacing(6)
        self.testsLayout.setObjectName("testsLayout")
        self.scrollArea_2.setWidget(self.testsLayoutWidget)
        self.verticalLayout_4.addWidget(self.scrollArea_2)
        self.horizontalLayout_4.addWidget(self.testFrame)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.stepsStartWidget = QtWidgets.QWidget(self.workPage)
        self.stepsStartWidget.setObjectName("stepsStartWidget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.stepsStartWidget)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.startStepsButton = QtWidgets.QPushButton(self.stepsStartWidget)
        self.startStepsButton.setObjectName("startStepsButton")
        self.horizontalLayout_6.addWidget(self.startStepsButton)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.horizontalLayout_5.addWidget(self.stepsStartWidget)
        self.testsStartWidget = QtWidgets.QWidget(self.workPage)
        self.testsStartWidget.setObjectName("testsStartWidget")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.testsStartWidget)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem6)
        self.startTestsButton = QtWidgets.QPushButton(self.testsStartWidget)
        self.startTestsButton.setObjectName("startTestsButton")
        self.horizontalLayout_7.addWidget(self.startTestsButton)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem7)
        self.horizontalLayout_5.addWidget(self.testsStartWidget)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.currentProgressBar = QtWidgets.QProgressBar(self.workPage)
        self.currentProgressBar.setEnabled(False)
        self.currentProgressBar.setProperty("value", 0)
        self.currentProgressBar.setTextVisible(True)
        self.currentProgressBar.setObjectName("currentProgressBar")
        self.verticalLayout_3.addWidget(self.currentProgressBar)
        self.overallProgressBar = QtWidgets.QProgressBar(self.workPage)
        self.overallProgressBar.setEnabled(False)
        self.overallProgressBar.setProperty("value", 0)
        self.overallProgressBar.setObjectName("overallProgressBar")
        self.verticalLayout_3.addWidget(self.overallProgressBar)
        self.stackedWidget.addWidget(self.workPage)
        self.verticalLayout_6.addWidget(self.stackedWidget)
        self.verticalLayout.addLayout(self.verticalLayout_6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.actionBarcode = QtWidgets.QAction(MainWindow)
        self.actionBarcode.setObjectName("actionBarcode")
        self.actionEnd = QtWidgets.QAction(MainWindow)
        self.actionEnd.setObjectName("actionEnd")

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        self.barcodeLineEdit.returnPressed.connect(MainWindow.checkBarcodeAndLoadRouter)
        self.scanButton.clicked.connect(MainWindow.checkBarcodeAndLoadRouter)
        self.backButton.clicked.connect(MainWindow.switchToBarcode)
        self.startTestsButton.clicked.connect(MainWindow.runTests)
        self.startStepsButton.clicked.connect(MainWindow.runSteps)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Turris Omnia - Router Tool Gui"))
        self.checkNeededLabel.setText(_translate("MainWindow", "Nutná kontrola stanoviště"))
        self.workstationTestLabel.setText(_translate("MainWindow", "TEST STANOVIŠTĚ"))
        self.label_3.setText(_translate("MainWindow", "RAM:"))
        self.ramLabel.setText(_translate("MainWindow", "?G"))
        self.label_7.setText(_translate("MainWindow", "Region:"))
        self.regionLabel.setText(_translate("MainWindow", "?"))
        self.titleLabel.setText(_translate("MainWindow", "Oživování a Testování"))
        self.label_2.setText(_translate("MainWindow", "Naskenujte kód:"))
        self.serialNumberLabel.setText(_translate("MainWindow", "#SERIAL NUMBER"))
        self.label_4.setText(_translate("MainWindow", "Oživování"))
        self.label_5.setText(_translate("MainWindow", "Testy"))
        self.startStepsButton.setText(_translate("MainWindow", "Začni Oživovat"))
        self.startTestsButton.setText(_translate("MainWindow", "Spusť testy"))
        self.overallProgressBar.setFormat(_translate("MainWindow", "%v/%m"))
        self.actionBarcode.setText(_translate("MainWindow", "&Barcode"))
        self.actionEnd.setText(_translate("MainWindow", "&Konec"))

import icons_rc
