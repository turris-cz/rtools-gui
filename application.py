import importlib
import logging
import os
import sys
import errno
import traceback

from PyQt5.QtWidgets import QApplication
from PyQt5.QtSql import QSqlDatabase

from custom_exceptions import IncorrectSerialNumber


# custom qApp
qApp = None

# settings module
settings = None

# db wrapper module
db_wrapper = None

# mock db wrapper module
db_wrapper_mock = None


def _printException(type, value, tb):
    type = "%s.%s" % (type.__module__, type.__name__)
    trace = "\n".join(traceback.format_tb(tb))
    qApp.loggerMain.error(
        "Exception occured:\n%s(\"%s\")\nTraceback:\n%s" % (type, value, trace))
    qApp.loggerMain.warn("Error occured. Exiting...")
    sys.exit(1)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        # load the settings module
        global settings
        settings_module = os.environ.get('RTOOLS_SETTINGS', 'settings.omnia')
        settings = importlib.import_module(settings_module)

        logging.root.setLevel(logging.INFO)
        logging.FileHandler(settings.LOG_APP_FILE)
        STDOUTFORMAT = '%(levelname)s %(message)s'
        FILEFORMAT = '%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
        fileFormatter = logging.Formatter(FILEFORMAT)
        fileHandler = logging.FileHandler(settings.LOG_APP_FILE)
        fileHandler.setFormatter(fileFormatter)
        stdoutHandler = logging.StreamHandler(sys.stdout)
        stdoutFormatter = logging.Formatter(STDOUTFORMAT)
        stdoutHandler.setFormatter(stdoutFormatter)
        self.loggerMain = logging.getLogger("MAIN")
        self.loggerMain.addHandler(fileHandler)
        self.loggerMain.addHandler(stdoutHandler)
        self.loggerDb = logging.getLogger("DB")
        self.loggerDb.addHandler(fileHandler)

        # This line will enable to handle exceptions outside of Qt event loop
        sys.excepthook = _printException

        # load the app link
        global qApp
        qApp = self

        # load workflow module
        self.workflow = importlib.import_module(settings.WORKFLOW_STEPS_MODULE)

        # load test module
        self.tests = importlib.import_module(settings.WORKFLOW_TESTS_MODULE)

        # load db module
        global db_wrapper
        db_wrapper = importlib.import_module(settings.DB_WRAPPER_MODULE)

        # load mock db wrapper module
        global db_wrapper_mock
        db_wrapper_mock = importlib.import_module(settings.DB_WRAPPER_MOCK_MODULE)

        # store tests/steps only options
        self.tests_only = '-t' in args[0] or '--tests-only' in args[0]
        self.steps_only = '-s' in args[0] or '--steps-only' in args[0]
        self.run_offline = False

        # init logging
        try:
            os.makedirs(os.path.dirname(settings.LOG_APP_FILE))
        except OSError as e:
            # Dir already exists continue
            if e.errno not in [errno.EEXIST]:
                raise e

        try:
            os.makedirs(os.path.dirname(settings.LOG_ROUTERS_DIR))
        except OSError as e:
            # Dir already exists continue
            if e.errno not in [errno.EEXIST]:
                raise e

        self.loggerMain.info("Application starting")
        self.loggerMain.info("Using settings '%s'" % settings_module)
        self.loggerMain.info("Using steps '%s'" % settings.WORKFLOW_STEPS_MODULE)
        self.loggerMain.info("Using tests '%s'" % settings.WORKFLOW_TESTS_MODULE)
        self.loggerMain.info("Using db wrapper '%s'" % settings.DB_WRAPPER_MODULE)

        # set the db connection
        if settings.DB is None:
            # don't use database in isolated environment
            self.loggerMain.info("Running in offline mode - not using database")
            self.connection = None
            self.run_offline = True
        else:
            self.connection = QSqlDatabase.addDatabase("QPSQL")
            self.connection.setHostName(settings.DB['HOST'])
            self.connection.setDatabaseName(settings.DB['NAME'])
            self.connection.setUserName(settings.DB['USER'])
            self.connection.setPassword(settings.DB['PASSWORD'])

        # current router
        self.router = None

    def useRouter(self, serialNumber):

        try:
            if int(serialNumber) in settings.WORKSTATION_TESTING_SERIALS:
                self.router = db_wrapper_mock.Router(serialNumber)

                # load workflow module
                self.workflow = importlib.import_module(settings.WORKFLOW_STEPS_WORKSTATION_MODULE)

                # load test module
                self.tests = importlib.import_module(settings.WORKFLOW_TESTS_WORKSTATION_MODULE)

                self.loggerMain.info("Using steps '%s'" % settings.WORKFLOW_STEPS_WORKSTATION_MODULE)
                self.loggerMain.info("Using tests '%s'" % settings.WORKFLOW_TESTS_WORKSTATION_MODULE)
                self.loggerMain.info("Using db wrapper '%s'" % settings.DB_WRAPPER_MOCK_MODULE)

            else:
                self.router = db_wrapper.Router(serialNumber)

                # load workflow module
                self.workflow = importlib.import_module(settings.WORKFLOW_STEPS_MODULE)

                # load test module
                self.tests = importlib.import_module(settings.WORKFLOW_TESTS_MODULE)

                self.loggerMain.info("Using steps '%s'" % settings.WORKFLOW_STEPS_MODULE)
                self.loggerMain.info("Using tests '%s'" % settings.WORKFLOW_TESTS_MODULE)
                self.loggerMain.info("Using db wrapper '%s'" % settings.DB_WRAPPER_MODULE)

        except ValueError:
            raise IncorrectSerialNumber

        return self.router

    def _canStartRunner(self):
        if hasattr(self, 'runner') and self.runner and self.runner.running:
            self.loggerMain.error("Other runner is already running!")
            return False
        return True

    def prepareTestRunner(self):
        if not self._canStartRunner():
            return None

        # Plan all tests
        self.testPlan = self.router.getTestPlan()

        if not self.testPlan:
            self.loggerMain.info("No tests can be performed for router '%s'" % self.router.id)
            return None

        # Note that runner needs to be a object member
        # otherwise it would be disposed its thread execution
        from runner import Runner
        self.runner = Runner(
            self.router.id, [self.tests.TESTS[i] for i in self.testPlan],
            Runner.TYPE_TESTS, self.router.testAttempt
        )

        return self.runner

    def prepareStepRunner(self):
        if not self._canStartRunner():
            return None

        self.stepPlan = self.router.getStepPlan()

        # Everything was performed. Skipping
        if not self.stepPlan:
            self.loggerMain.info(
                "All steps were performed for router '%s (%s)'"
                % (self.router.id, self.router.idHex)
            )
            return None

        # Note that runner needs to be a object member
        # otherwise it would be disposed its thread execution
        from runner import Runner
        self.runner = Runner(
            self.router.id, [self.workflow.WORKFLOW[i] for i in self.stepPlan],
            Runner.TYPE_STEPS, self.router.stepAttempt
        )

        return self.runner
