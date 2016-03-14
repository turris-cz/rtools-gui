import importlib
import os

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

        # TODO init logging here

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
