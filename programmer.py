# -*- coding: utf8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy
from ui.programmer import Ui_Programmer
import qrc.icons

from utils import MAX_SERIAL_LEN

from application import qApp, settings
from moxtester import MoxTester, MoxTesterException
from workflow import WorkFlow, WorkflowException


class ProgrammerWidget(QtWidgets.QFrame, Ui_Programmer):
    WORK_STATE_FAILED = "F"
    WORK_STATE_UNKNOWN = "U"
    WORK_STATE_PASSED = "P"
    WORK_STATE_RUNNING = "R"
    WORK_STATES = (
        WORK_STATE_FAILED,
        WORK_STATE_UNKNOWN,
        WORK_STATE_PASSED,
        WORK_STATE_RUNNING,
    )

    def __init__(self, mainWindow, index):
        self.mainWindow = mainWindow
        self.index = index

        super(ProgrammerWidget, self).__init__()
        self.setupUi(self)  # create gui
        self.barcodeLineEdit.setMaxLength(MAX_SERIAL_LEN)
        self.indexLabel.setText("Programátor: " + str(index + 1))
        self.intro_error(None)
        self._steps = []  # List of steps elements

        self.workflow = None  # Current workflow for this programmer
        self.programmer = None  # Handle for MoxTester
        self.connectProgrammer()

    def intro_error(self, message):
        "Display error for intro page. Pass None to reset previous error."
        self.introMessageLabel.setVisible(message is None)
        self.introErrorLabel.setVisible(message is not None)
        if message is not None:
            self.introErrorLabel.setText(message)

    def select(self):
        "Try to select this programmer for new board session"
        if self.programmer is None:
            self.mainWindow.display_msg(
                "Programátor {} zřejmě není připojen".format(self.index + 1))
            return
        if self.workflow is not None:
            self.mainWindow.display_msg(
                "Programátor {} je aktuálně obsazen".format(self.index + 1))
            return
        self.programmer.reset_tester()
        if not self.programmer.board_present():
            self.mainWindow.display_msg(
                "Do programátoru {} není vložená deska".format(self.index + 1))
            return
        self.contentWidget.setCurrentWidget(self.pageIntro)
        self.introWidget.setCurrentWidget(self.pageIntroSerial)
        self.barcodeLineEdit.setFocus()

    @QtCore.pyqtSlot()
    def connectProgrammer(self):
        try:
            self.programmer = MoxTester(self.index)
            self.programmer.selftest()
        except MoxTesterException:
            # TODO print error to log
            # Ok this failed so we don't have programmer
            pass
        if self.programmer is not None:
            self.introWidget.setCurrentWidget(self.pageIntroReady)

    @QtCore.pyqtSlot()
    def barcodeScanEnter(self):
        """Slot called when barcode is scanned to input box. Should check if
        given code is valid and start flashing process"""
        serial_number = int(self.barcodeLineEdit.text())
        self.barcodeLineEdit.clear()
        self.mainWindow.refocus()
        if (serial_number >> 32) == 0xFFFFFFFF:
            self.intro_error("Naskenován kód programátoru")
            self.introWidget.setCurrentWidget(self.pageIntroReady)
            return
        try:
            self.workflow = WorkFlow(None, self.programmer, serial_number)
        except WorkflowException as e:
            self.workflow = None
            self.intro_error(str(e))
            self.introWidget.setCurrentWidget(self.pageIntroReady)
            return

        # Connect workflow signals to our slots
        self.workflow.singleProgressUpdate.connect(
            self.currentProgress.setValue)
        self.workflow.allProgressUpdate.connect(self.totalProgress.setValue)
        self.workflow.setStepState.connect(self.stepStateUpdate)
        self.workflow.uartLogUpdate.connect(self.uartOutput)
        self.workflow.workflow_exit.connect(self.workflowExit)

        # Update GUI
        self.serialNumberLabel.setText(hex(serial_number))
        self.typeLabel.setText(self.workflow.get_board_name())
        self.contentWidget.setCurrentWidget(self.pageWork)
        self.progressWidget.setCurrentWidget(self.progressProgress)
        self._steps = []
        self.ProgressContent.layout().takeAt(0)  # Drop all step widgets
        for step in self.workflow.get_steps():
            self._new_step(step)
        self.totalProgress.setMaximum(len(self._steps))  # Set max to progress bar
        # Add spacers
        self.ProgressContent.layout().addItem(
            QtWidgets.QSpacerItem(
                0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            len(self._steps), 0
            )
        self.ProgressContent.layout().addItem(
            QtWidgets.QSpacerItem(
                0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
            len(self._steps), 1
            )
        self.ProgressContent.layout().addItem(
            QtWidgets.QSpacerItem(
                0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            len(self._steps), 4
            )

        self.workflow.run()  # And lastly start worklow

    def _new_step(self, step):
        icon = QtWidgets.QLabel(self.ProgressContent)
        icon.setMinimumSize(16, 16)
        icon.setMaximumSize(16, 16)
        self.ProgressContent.layout().addWidget(icon, len(self._steps), 1)
        label = QtWidgets.QLabel(self.ProgressContent)
        label.setText(step['name'])
        self.ProgressContent.layout().addWidget(label, len(self._steps), 2)
        self._steps.append({
            "icon": icon,
            "label": label,
            })
        self.stepStateUpdate(len(self._steps) - 1, step['state'], None)

    @QtCore.pyqtSlot()
    def barcodeAbandon(self):
        """Slot called when input box for barcode is abandoned. It closes
        current state and returns to intro page"""
        self.barcodeLineEdit.clear()
        self.introWidget.setCurrentWidget(self.pageIntroReady)
        self.mainWindow.refocus()

    @QtCore.pyqtSlot(int, str, str)
    def stepStateUpdate(self, step, state, msg):
        """Set state of one of steps. state is string and can be one of
        supported steps from workflow.
        """
        _STATE_TO_PIX = {
            WorkFlow.STEP_UNKNOWN: ":/img/icons/unknown.png",
            WorkFlow.STEP_RUNNING: ":/img/icons/run.png",
            WorkFlow.STEP_FAILED: ":/img/icons/fail.png",
            WorkFlow.STEP_OK: ":/img/icons/ok.png",
            WorkFlow.STEP_UNSTABLE: ":/img/icons/unstable.png",
        }
        self._steps[step]['icon'].setPixmap(
            QtGui.QPixmap(_STATE_TO_PIX[state])
            )
        # TODO show warnings somewhere

    @QtCore.pyqtSlot(str)
    def uartOutput(self, line):
        """Update UART log with given new line.
        """
        # TODO
        pass

    @QtCore.pyqtSlot(str)
    def workflowExit(self, error):
        """Slot called when workflow exits. If workflow exited with error then
        error is string with error message. If error is None then there was no
        error.
        """
        self.workflow = None
        if not error:
            self.contentWidget.setCurrentWidget(self.pageIntro)
        else:
            self.progressWidget.setCurrentWidget(self.progressError)
            self.progressErrorLabel.setText(error)
