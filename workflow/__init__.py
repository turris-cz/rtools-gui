from PyQt5 import QtCore
from .exceptions import WorkflowException
from .exceptions import InvalidBoardNumberException


class WorkFlow(QtCore.QObject):
    "General class managing workflow for single programmer and board."
    _BOARD_MAP = {
        0x30: "Core (A)",
        0x31: "SFP (D)",
        0x32: "PCI (B)",
        0x33: "Topaz - 4x ethernet (C)",
        0x34: "Peridot - 8x ethernet (E)",
        0x35: "USB (F)",
        0x36: "PCI pass-trough (G)",
        }

    singleProgressUpdate = QtCore.pyqtSignal(int)
    allProgressUpdate = QtCore.pyqtSignal(int)
    setRunning = QtCore.pyqtSignal(int)
    setFailed = QtCore.pyqtSignal(int)
    setCompleted = QtCore.pyqtSignal(int)
    uartLogUpdate = QtCore.pyqtSignal(str)

    def __init__(self, db_connection, moxtester, serial_number):
        super().__init__()
        self.db_connection = db_connection
        self.moxtester = moxtester
        self.serial_number = serial_number

        self.series = serial_number >> 32
        if self.series == 0xFFFFFFFF or self.series < 0xD:
            raise InvalidBoardNumberException(
                "Serial number does not seems to have valid series for Mox: " + hex(self.series))
        self.board_id = (serial_number >> 24) & 0xff
        if self.board_id not in self._BOARD_MAP:
            raise InvalidBoardNumberException(
                "Unsupported board ID in serial number: " + hex(self.board_id))

        # TODO load steps
        self.steps = []

        self.thread = QtCore.QThread(self)

    def get_steps(self):
        """Returns table steps. Every step is a dictionary where following keys
        exists:
            * name: name of single step
            * description: long description of what is happening when this step
              is being executed
            * completed: boolean value if step was already once completed
            * success: boolean value if steap completed succesfully
        """
        # TODO aggregate
        return self.steps

    def get_board_name(self):
        """Returns name of board"""
        return self._BOARD_MAP[self.board_id]

    def run(self):
        "Trigger workflow execution"
        # TODO
        pass
