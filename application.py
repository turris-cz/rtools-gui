import importlib
import logging
import os
import sys
import errno
import traceback

from PyQt5.QtWidgets import QApplication
from PyQt5.QtSql import QSqlDatabase


# custom qApp
qApp = None

# settings module
settings = None

# workflow module
workflow = None

# tests module
tests = None


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

        # This line will enable to handle exceptions outside of Qt event loop
        sys.excepthook = _printException

        # load the app link
        global qApp
        qApp = self

        # load the settings module
        global settings
        settings_module = os.environ.get('RTOOLS_SETTINGS', 'settings.omnia')
        settings = importlib.import_module(settings_module)

        # load workflow module
        global workflow
        workflow = importlib.import_module(settings.WORKFLOW_STEPS_MODULE)

        # load test module
        global tests
        tests = importlib.import_module(settings.WORKFLOW_TESTS_MODULE)

        # init logging
        try:
            os.makedirs(os.path.dirname(settings.LOG_APP_FILE))
        except OSError as e:
            # Dir already exists continue
            if e.errno not in [errno.EEXIST]:
                raise e

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

        # set the db connection
        self.connection = QSqlDatabase.addDatabase("QPSQL")
        self.connection.setHostName(settings.DB['HOST'])
        self.connection.setDatabaseName(settings.DB['NAME'])
        self.connection.setUserName(settings.DB['USER'])
        self.connection.setPassword(settings.DB['PASSWORD'])

        # current router
        self.router = None

    def useRouter(self, serialNumber):

        from db_wrapper import Router
        self.router = Router(serialNumber)

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
            self.router.id, [tests.TESTS[i] for i in self.testPlan], self.router.currentRun,
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
            self.router.id, [workflow.WORKFLOW[i] for i in self.stepPlan],
            self.router.currentRun, Runner.TYPE_STEPS, self.router.stepAttempt
        )

        return self.runner
