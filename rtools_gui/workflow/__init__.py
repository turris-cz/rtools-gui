import traceback
from time import sleep
from PyQt5 import QtCore
from .. import db
from .exceptions import WorkflowException
from .exceptions import InvalidBoardNumberException
from .a import ASTEPS
from .b import BSTEPS
from .c import CSTEPS
from .d import DSTEPS
from .e import ESTEPS

_BOARD_MAP = {
    0x30: {
        "name": "Core (A)",
        "steps": ASTEPS,
        },
    0x31: {
        "name": "SFP (D)",
        "steps": DSTEPS,
        },
    0x32: {
        "name": "PCI (B)",
        "steps": BSTEPS,
        },
    0x33: {
        "name": "Topaz - 4x ethernet (C)",
        "steps": CSTEPS,
        },
    0x34: {
        "name": "Peridot - 8x ethernet (E)",
        "steps": ESTEPS,
        },
    #0x35: {
    #    "name": "USB (F)",
    #    "steps": [],
    #    },
    #0x36: {
    #    "name": "PCI pass-trough (G)",
    #    "steps": [],
    #    },
    }


class WorkFlow(QtCore.QObject):
    "General class managing workflow for single programmer and board."
    STEP_UNKNOWN="unknown" # Step was not run yet
    STEP_RUNNING="running" # Currently executing
    STEP_FAILED="failed" # Execution failed
    STEP_OK="ok" # Execution exited normally
    STEP_UNSTABLE="unstable" # Step that previous run successfully but should run again

    singleProgressUpdate = QtCore.pyqtSignal(int)
    allProgressUpdate = QtCore.pyqtSignal(int, int)
    setStepState = QtCore.pyqtSignal(int, str, str)
    uartLogUpdate = QtCore.pyqtSignal(str)
    workflow_exit = QtCore.pyqtSignal(str)

    def __init__(self, conf, db_connection, db_programmer_state, resources, moxtester, serial_number):
        super().__init__()
        self.conf = conf
        self.db_connection = db_connection
        self.db_programmer_state = db_programmer_state
        self.db_board = None
        self.db_run = None
        self.moxtester = moxtester
        self.serial_number = serial_number

        # Verify board serial number
        self.series = serial_number >> 32
        if self.series == 0xFFFFFFFF or self.series < 0xD:
            raise InvalidBoardNumberException(
                "Serial number does not seems to have valid series for Mox: " + hex(self.series))
        self.board_id = (serial_number >> 24) & 0xff
        if self.board_id not in _BOARD_MAP:
            raise InvalidBoardNumberException(
                "Unsupported board ID in serial number: " + hex(self.board_id))
        # Get board from database
        self.db_board = db.Board(db_connection, serial_number)

        # Load steps
        self.steps = [
            step(moxtester, conf, resources, self.singleProgressUpdate.emit)
            for step in _BOARD_MAP[self.board_id]['steps']]

        self.thread = QtCore.QThread(self)

    def get_steps(self):
        """Returns table steps. Every step is a dictionary where following keys
        exists:
            * name: name of single step
            * state: value signaling step state which is one of STEP_ constants
        """
        steps = []
        for step in self.steps:
            steps.append({
                'name': step.name(),
                'state': self.STEP_UNKNOWN,
                })
        return steps

    def get_board_name(self):
        """Returns name of board"""
        return _BOARD_MAP[self.board_id]['name']

    def run(self):
        "Trigger workflow execution"
        self.moveToThread(self.thread)
        self.thread.started.connect(self._run)
        self.thread.start()

    def _run_exit(self, error=None):
        "Helper function for _run cleanup"
        self.db_run.finish(error is None)
        self.workflow_exit.emit(None if error is None else str(error))
        self.moxtester.default()  # Return moxtester to default safe setting
        self.thread.quit()

    def _run(self):
        "Workflow executor"
        self.db_run = db.ProgrammerRun(
            self.db_connection, self.db_board, self.db_programmer_state,
            self.moxtester.chip_id, [x.dbid() for x in self.steps])

        self.allProgressUpdate.emit(0, len(self.steps))
        sleep(0.1)  # Give some time to GUI to catch up
        for i in range(len(self.steps)):
            db_step = db.ProgrammerStep(
                self.db_connection, self.db_run, self.steps[i].dbid())
            step = self.steps[i]
            try:
                self.setStepState.emit(i, self.STEP_RUNNING, "")
                msg = step.run()
                self.allProgressUpdate.emit(i + 1, len(self.steps))
                if msg is None:
                    self.setStepState.emit(i, self.STEP_OK, "")
                else:
                    self.setStepState.emit(i, self.STEP_WARNING, msg)
                db_step.finish(msg is None, msg)
            except Exception as e:
                trc = traceback.format_exc()
                # TODO logging
                print(trc)
                db_step.finish(False, str(trc))
                self.setStepState.emit(i, self.STEP_FAILED, str(e))
                self._run_exit(e)
                return
        self._run_exit()
