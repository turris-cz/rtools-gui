import psycopg2
from .exceptions import DBException

DB_USER = "mox_rtools"
DB_PASSWORD = "VI7QNfDvJtmnrpQ5"
DB_NAME = "mox_boards"


def connect():
    """Connect application to database
    Returns connection handle to database.
    """
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)


# Note: Following classes are written so that by instantiating them you create
# new records in database. Then new object is used to reference that record to
# other classes in this module.

class _GenericTable:
    "Generic table representation in this module"

    def __init__(self, db_connection):
        self._dbc = db_connection
        self._cur = db_connection.cursor()

    # TODO make all commits to not throw exception and instead write them to
    # recovery file.


class Board(_GenericTable):
    "Database representation for single board"
    _SELECT_TYPE = "SELECT type FROM boards WHERE serial = %s;"
    _INSERT_CORE_KEY = "INSERT INTO core_keys (board, key) VALUES (%s, %s);"
    _SELECT_CORE_KEY = "SELECT key FROM core_keys WHERE board = %s;"

    def __init__(self, db_connection, serial_number):
        super().__init__(db_connection)
        self.serial = serial_number

        self._cur.execute(self._SELECT_TYPE, (serial_number,))
        res = self._cur.fetchone()
        if res is None:
            raise DBException(
                "There is no such board in database: " + hex(serial_number))
        self.type = res[0]

    def set_core_key(self, key):
        """Record public key for this board."""
        if self.type != "A":
            raise DBException(
                "Invalid board type for inserting core key: " + str(self.type))
        self._cur.execute(self._INSERT_CORE_KEY, (self.serial, str(key)))
        self._dbc.commit()

    def core_key(self):
        """Returns core key for this board. If there is no such key then
        returns None."""
        self._cur.execute(self._SELECT_CORE_KEY, (self.serial,))
        res = self._cur.fetchone()
        return None if res is None else res[0]


class ProgrammerState(_GenericTable):
    "Database connection for programmer_state"
    _SELECT_PROGRAMMER_ID = """SELECT id FROM programmer_state WHERE
        hostname = %s AND rtools_hash = %s AND secure_firmware = %s AND
        uboot = %s AND rescue = %s AND dtb = %s;"""
    _INSERT_PROGRAMMER_ID = """INSERT INTO programmer_state
        (hostname, rtools_hash, secure_firmware, uboot, rescue, dtb) VALUES
        (%s, %s, %s, %s, %s, %s) RETURNING id;"""

    def __init__(self, db_connection, resources):
        super().__init__(db_connection)
        state_data = (
            resources.hostname, resources.rtools_head,
            resources.secure_firmware_hash, resources.uboot_hash,
            resources.rescue_hash, resources.dtb_hash)
        # Look for existing programmer state
        self._cur.execute(self._SELECT_PROGRAMMER_ID, state_data)
        state = self._cur.fetchone()
        if state is None:
            # If not found then create new one
            self._cur.execute(self._INSERT_PROGRAMMER_ID, state_data)
            state = self._cur.fetchone()
            self._dbc.commit()
        # Record id of current programmer state
        self.id = state[0]


class ProgrammerRun(_GenericTable):
    "Database representation for single run"
    _INSERT_RUN = """INSERT INTO runs
        (board, programmer, programmer_id, steps) VALUES
        (%s, %s, %s, %s) RETURNING id;
        """
    _UPDATE_FINISH = """UPDATE runs SET success = %s, tend = current_timestamp
        WHERE id = %s;
        """

    def __init__(self, db_connection, board, programmer_state, programmer_id, steps):
        super().__init__(db_connection)
        self.finished = False
        self._cur.execute(
            self._INSERT_RUN,
            (board.serial, programmer_state.id, programmer_id, steps))
        self._dbc.commit()
        self.id = self._cur.fetchone()[0]

    def finish(self, success):
        "Mark this run as finished."
        if self.finished:
            raise DBException("Run is already finished")
        self._cur.execute(self._UPDATE_FINISH, (bool(success), self.id))
        self._dbc.commit()
        self.finished = True


class ProgrammerStep(_GenericTable):
    "Database reprepsentation of single step in some run"
    _INSERT_STEP = """INSERT INTO steps (step_name, run) VALUES
        (%s, %s) RETURNING id;
        """
    _UPDATE_FINISH = """UPDATE steps SET
        success = %s, message = %s, tend = current_timestamp WHERE id = %s;
        """

    def __init__(self, db_connection, run, step_name):
        super().__init__(db_connection)
        self.finished = False
        self._cur.execute(self._INSERT_STEP, (step_name, run.id))
        self._dbc.commit()
        self.id = self._cur.fetchone()[0]

    def finish(self, success, message=None):
        "Mark this step as finished."
        if self.finished:
            raise DBException("Step is already finished")
        self._cur.execute(
            self._UPDATE_FINISH,
            (bool(success), message, self.id))
        self._dbc.commit()
        self.finished = True
