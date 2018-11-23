import psycopg2
from .exceptions import DBException


def connect(cnf):
    """Connect application to database
    Returns connection handle to database.
    """
    parameters = {}
    parameters['dbname'] = cnf.db_database
    if cnf.db_user is not None:
        parameters['user'] = cnf.db_user
    if cnf.db_password is not None:
        parameters['password'] = cnf.db_password
    if cnf.db_host is not None:
        parameters['host'] = cnf.db_host
    if cnf.db_port is not None:
        parameters['port'] = cnf.db_port
    return psycopg2.connect(**parameters)


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
    _SELECT_MAC_WAN = "SELECT mac_wan FROM boards WHERE serial = %s;"
    _SELECT_MAC_SGMII = "SELECT mac_sgmii FROM boards WHERE serial = %s;"
    _SELECT_REVISION = "SELECT revision FROM boards WHERE serial = %s;"
    _INSERT_CORE_INFO = """INSERT INTO core_info (serial, mem_size, key) VALUES
        (%s, %s, %s);"""
    _COUNT_CORE_INFO = """SELECT count(1) FROM core_info WHERE
        serial = %s AND mem_size = %s AND key = %s;"""
    _SELECT_CORE_MEM_SIZE = "SELECT mem_size FROM core_info WHERE board = %s;"
    _SELECT_CORE_KEY = "SELECT key FROM core_info WHERE board = %s;"

    def __init__(self, db_connection, serial_number):
        super().__init__(db_connection)
        self.serial = serial_number

        self._cur.execute(self._SELECT_TYPE, (serial_number,))
        res = self._cur.fetchone()
        if res is None:
            raise DBException(
                "There is no such board in database: " + hex(serial_number))
        self.type = res[0]

    def mac_wan(self):
        "Returns mac address for wan interface"
        self._cur.execute(self._SELECT_MAC_WAN, (self.serial,))
        res = self._cur.fetchone()
        return None if res is None else res[0]

    def mac_sgmii(self):
        "Returns mac address for sgmii interface (moxtet ethernet interface)"
        self._cur.execute(self._SELECT_MAC_SGMII, (self.serial,))
        res = self._cur.fetchone()
        return None if res is None else res[0]

    def revision(self):
        "Numeric identifier of revision"
        self._cur.execute(self._SELECT_REVISION, (self.serial,))
        res = self._cur.fetchone()
        return None if res is None else int(res[0])

    def set_core_info(self, mem, key):
        """Record public key and memory size for this board."""
        if self.type != "A":
            raise DBException(
                "Invalid board type for inserting core info: " + str(self.type))
        self._cur.execute(self._COUNT_CORE_INFO, (self.serial, mem, str(key)))
        if self._cur.fetchone()[0] > 0:
            return  # This one is already recorded
        # TODO what it there is record for this serial number but with
        # different key or memory size
        self._cur.execute(self._INSERT_CORE_INFO, (self.serial, mem, str(key)))
        self._dbc.commit()

    def core_mem(self):
        """Returns core memory size for this board. If there is no such key
        then returns None."""
        self._cur.execute(self._SELECT_CORE_MEM_SIZE, (self.serial,))
        res = self._cur.fetchone()
        return None if res is None else int(res[0])

    def core_key(self):
        """Returns core key for this board. If there is no such key then
        returns None."""
        self._cur.execute(self._SELECT_CORE_KEY, (self.serial,))
        res = self._cur.fetchone()
        return None if res is None else res[0]


class ProgrammerState(_GenericTable):
    "Database connection for programmer_state"
    _SELECT_PROGRAMMER_ID = """SELECT id FROM programmer_state WHERE
        hostname = %s AND rtools_git = %s AND moximager_git = %s AND
        moximager_hash = %s AND secure_firmware = %s AND uboot = %s AND
        rescue = %s AND dtb = %s;"""
    _INSERT_PROGRAMMER_ID = """INSERT INTO programmer_state
        (hostname, rtools_git, moximager_git, moximager_hash, secure_firmware,
        uboot, rescue, dtb) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""

    def __init__(self, db_connection, resources):
        super().__init__(db_connection)
        state_data = (
            resources.hostname, resources.rtools_git, resources.mox_imager_git,
            resources.mox_imager_hash, resources.secure_firmware_hash,
            resources.uboot_hash, resources.rescue_hash, resources.dtb_hash)
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
    _INSERT_RESULT = "INSERT INTO run_results (id, success) VALUES (%s, %s);"

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
        self._cur.execute(self._INSERT_RESULT, (self.id, bool(success)))
        self._dbc.commit()
        self.finished = True


class ProgrammerStep(_GenericTable):
    "Database reprepsentation of single step in some run"
    _INSERT_STEP = """INSERT INTO steps (step_name, run) VALUES
        (%s, %s) RETURNING id;
        """
    _INSERT_RESULT = """INSERT INTO step_results (id, success, message) VALUES
        (%s, %s, %s);
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
            self._INSERT_RESULT,
            (self.id, bool(success), message))
        self._dbc.commit()
        self.finished = True
