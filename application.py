import importlib
import logging
import os
import errno

from PyQt5.QtWidgets import QApplication
from PyQt5.QtSql import QSqlDatabase


# custom qApp
qApp = None

# settins module
settings = None

# workflow module
workflow = None

# tests module
tests = None


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

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
        LOGFORMAT = '%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
        logFormatter = logging.Formatter(LOGFORMAT)
        fh = logging.FileHandler(settings.LOG_APP_FILE)
        fh.setFormatter(logFormatter)
        self.loggerMain = logging.getLogger("MAIN")
        self.loggerMain.addHandler(fh)
        self.loggerDb = logging.getLogger("DB")
        self.loggerDb.addHandler(fh)

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
        # TODO log setting the router here

        from db_wrapper import Router
        self.router = Router(serialNumber)

        return self.router

    def prepareTestRunner(self):
        from runner import Runner
        # Plan all tests
        self.testPlan = range(len(tests.TESTS))

        if not self.testPlan:
            self.loggerMain.info("No tests can be performed for router '%s'" % qApp.router.id)
            return None

        # Note that runner needs to be a object member
        # otherwise it would be disposed its thread execution
        self.testRunner = Runner([tests.TESTS[i] for i in self.testPlan])

        return self.testRunner

    def prepareStepRunner(self):
        # filter workflow (skipped passed)
        self.stepPlan = [
            i for i in range(len(workflow.WORKFLOW))
            if not workflow.WORKFLOW[i].name in self.router.performedSteps['passed']
        ]

        # Everything was performed. Skipping
        if not self.stepPlan:
            self.loggerMain.info(
                "All steps were performed for router '%s (%s)'"
                % (qApp.router.id, qApp.router.idHex)
            )
            return None

        # Note that runner needs to be a object member
        # otherwise it would be disposed its thread execution
        from runner import Runner
        self.stepRunner = Runner([workflow.WORKFLOW[i] for i in self.stepPlan])

        return self.stepRunner
