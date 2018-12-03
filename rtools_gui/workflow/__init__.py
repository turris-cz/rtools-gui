from threading import Thread
from .. import db, report
from .exceptions import InvalidBoardNumberException
from .a import ASTEPS
from .b import BSTEPS
from .c import CSTEPS
from .d import DSTEPS
from .e import ESTEPS
from .f import FSTEPS
from .g import GSTEPS

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
                 resources, moxtester, serial_number):
        super().__init__()
        self.handler = handler
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
            raise InvalidBoardNumberException("Serial number does not seems to have valid series for Mox: " + hex(self.series))
        self.board_id = (serial_number >> 24) & 0xff
        if self.board_id not in _BOARD_MAP:
            raise InvalidBoardNumberException(
                "Unsupported board ID in serial number: " + hex(self.board_id))
        # Get board from database
        self.db_board = db.Board(db_connection, serial_number)

        # Load steps
        self.steps = [
            step(serial_number, moxtester, conf, resources, self.db_board,
                 handler.progress_step) for step in
            _BOARD_MAP[self.board_id]['steps']]
        # Create thread
        self.thread = Thread(
            target=self._run, name="workflow-" + str(serial_number),
            daemon=True)

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
        db_run = db.ProgrammerRun(
            self.db_connection, self.db_board, self.db_programmer_state,
            self.moxtester.chip_id, [x.id() for x in self.steps])
        error_str = None
        for step in self.steps:
            db_step = db.ProgrammerStep(
                self.db_connection, db_run, step.id())
            try:
                self.handler.step_update(step.id(), self.STEP_RUNNING)
                msg = step.run()
                db_step.finish(msg is None, msg)
                # TODO display warning message in graphics and report it
                self.handler.step_update(step.id(), self.STEP_OK)
            except Exception as e:
                report.ignored_exception()
                db_step.finish(False, str(e))
                self.handler.step_update(step.id(), self.STEP_FAILED)
                error_str = str(e)
                break  # Do not continue after exception in workflow
        db_run.finish(error_str is None)
        self.handler.workflow_exit(None if error_str is None else error_str)
        self.moxtester.default()  # Return moxtester to default safe setting
