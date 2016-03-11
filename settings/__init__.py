import os
import importlib

from PyQt5.QtSql import QSqlDatabase

settings_module = os.environ.get('RTOOLS_SETTINGS', 'settings.omnia')
settings = importlib.import_module(settings_module)

workflow = importlib.import_module(settings.WORKFLOW_MODULE)
tests = importlib.import_module(settings.TESTS_MODULE)

# TODO prepare logging

# set DB connection
connection = QSqlDatabase.addDatabase("QPSQL")
connection.setHostName(settings.DB['HOST'])
connection.setDatabaseName(settings.DB['NAME'])
connection.setUserName(settings.DB['USER'])
connection.setPassword(settings.DB['PASSWORD'])

__all__ = ['settings', 'tests', 'workflow', 'connection']
