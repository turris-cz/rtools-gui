from threading import Thread
from pexpect import TIMEOUT
from .. import db, report
from .exceptions import InvalidBoardNumberException, RandomErrorException
from .a import ASTEPS
from .b import BSTEPS
from .c import CSTEPS
from .d import DSTEPS
from .e import ESTEPS
from .f import FSTEPS
from .g import GSTEPS
from .ripe import RSTEPS
import logging

_BOARD_MAP = {
    0x00: {  # TODO more reasonable CODE
        "name": "Ripe Atlas",
        "steps": RSTEPS,
    },
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
    0x35: {
        "name": "USB (F)",
        "steps": FSTEPS,
    },
    0x36: {
        "name": "PCI pass-trough (G)",
        "steps": GSTEPS,
    },
}

class WorkFlowHandler:
    "Abstract handler for workflow reported events"

    def progress_step(self, value):
        "Report progress of single step. value is float between 0 and 1."
        raise NotImplementedError

    def step_update(self, step_id, state):
        """Report step state update. state argument can be one of STEP_* values
        from WorkFlow class. step_id argument is identifier of updated step."""
        raise NotImplementedError

    def workflow_exit(self, error=None):
        """Called on workflow conclusion. Either there was no error and in that
        case argument error is set to None. If there was an error then argument
        error contains string describing it."""
        raise NotImplementedError


class WorkFlow:
    "General class managing workflow for single programmer and board."
    STEP_UNKNOWN = "unknown"  # Step was not run yet
    STEP_RUNNING = "running"  # Currently executing
    STEP_FAILED = "failed"  # Execution failed
    STEP_OK = "ok"  # Execution exited normally
    STEP_UNSTABLE = "unstable"  # Step exited with warnings

    def __init__(self, handler, conf, db_connection, db_programmer_state,
                 resources, moxtester, serial_number, mac_wan):
        super().__init__()
        self.handler = handler
        self.conf = conf
        self.db_connection = db_connection
        self.db_programmer_state = db_programmer_state
        self.db_board = None
        self.db_run = None
        self.moxtester = moxtester

        # Get board from database
        self.db_board = db.Board(db_connection, serial_number, mac_wan)
        self.serial_number = self.db_board.serial

        # Verify board serial number
        self.series = self.serial_number >> 32
        if self.series == 0xFFFFFFFF or self.series < 0xD:
            raise InvalidBoardNumberException("Serial number does not seems to have valid series for Mox: " + hex(self.series))
        self.board_id = (self.serial_number >> 24) & 0xff
        if self.board_id not in _BOARD_MAP:
            raise InvalidBoardNumberException(
                "Unsupported board ID in serial number: " + hex(self.board_id))

        # Load steps
        self.steps = [
            step(self.serial_number, moxtester, conf, resources, self.db_board,
                 handler.progress_step) for step in
            _BOARD_MAP[self.board_id]['steps']]
        # Create thread
        self.thread = Thread(
            target=self._run, name="workflow-" + str(self.serial_number),
            daemon=True)
        report.log("Workflow initialized on programmer {} for board {}".format(
            moxtester.tester_id, hex(self.serial_number)))

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
                'id': step.id(),
                'state': self.STEP_UNKNOWN,
            })
        return steps

    def get_board_name(self):
        """Returns name of board"""
        return _BOARD_MAP[self.board_id]['name']

    def start(self):
        "Trigger workflow execution"
        self.thread.start()

    def _run(self):
        "Workflow executor"
        core_info = self.db_board.core_info(self.serial_number)
        if core_info is not None:
            error_str = "Board {} on programmer {} already exists.".format(hex(self.serial_number),self.moxtester.tester_id)
            report.log(error_str)
        else:
            report.log("Workflow started on programmer {} for board {}".format(
                self.moxtester.tester_id, hex(self.serial_number)))
            db_run = db.ProgrammerRun(
                self.db_connection, self.db_board, self.db_programmer_state,
                self.moxtester.tester_id, [x.id() for x in self.steps])
            error_str = None
            i = 0
            retry = 0
            while i < len(self.steps):
                self.handler.reset_steps()
                db_step = db.ProgrammerStep(
                    self.db_connection, db_run, self.steps[i].id())
                try:
                    self.handler.workflow_update(i+0.1)
                    self.handler.step_update(self.steps[i].id(), self.STEP_RUNNING)
                    msg = self.steps[i].run()
                    db_step.finish(msg is None, msg)
                    if msg is not None:
                        report.log("Step {} on programmer {} for board {} warning: {}".format(
                            self.steps[i].id(), self.moxtester.tester_id, hex(self.serial_number), msg))
                    # TODO display warning message in graphics
                    self.handler.workflow_update(i)
                    self.handler.step_update(self.steps[i].id(), self.STEP_OK)
                    i=i+1
                except Exception as e:
                    if((isinstance(e,RandomErrorException) or (isinstance(e,TIMEOUT))) and retry <10):
                        report.log("Step {} on programmer {} for board {} failed: {}".format(
                            self.steps[i].id(), self.moxtester.tester_id, hex(self.serial_number), str(e)))
                        i = 0
                        retry += 1
                        report.log("Restarting the workflow - {}. retry".format(retry))
                        for step in self.steps:
                            step.state = self.STEP_UNKNOWN
                            self.handler.workflow_update(0)
                            self.handler.step_update(step.id(), self.STEP_UNKNOWN)
                        error_str = None
                    else:
                        report.ignored_exception()
                        db_step.finish(False, str(e))
                        self.handler.step_update(self.steps[i].id(), self.STEP_FAILED)
                        error_str = str(e)
                        report.log("Step {} on programmer {} for board {} failed: {}".format(
                            self.steps[i].id(), self.moxtester.tester_id, hex(self.serial_number), error_str))
                        break  # Do not continue after exception in workflow
            db_run.finish(error_str is None)
        self.moxtester.default()  # Return moxtester to default safe setting
        report.log("Workflow ended on programmer {} for board {}".format(
            self.moxtester.tester_id, hex(self.serial_number))
        )
        self.handler.workflow_exit(None if error_str is None else error_str)
