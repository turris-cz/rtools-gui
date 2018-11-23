import sys
import traceback
from PyQt5.QtWidgets import QApplication
from . import guard, resources, db
from .conf import Configs


def _printException(type, value, tb):
    type = "%s.%s" % (type.__module__, type.__name__)
    trace = "\n".join(traceback.format_tb(tb))
    print(
        "Exception occured:\n%s(\"%s\")\nTraceback:\n%s" % (type, value, trace))
    print("Error occured. Exiting...")
    sys.exit(1)


def main():
    conf = Configs()

    with guard.Guard():
        app = QApplication(sys.argv)

        # Load all resources
        res = resources.Resources(conf)
        # Connect to database
        dbconn = db.connect(conf)
        # Programmer state
        dbprg_state = db.ProgrammerState(dbconn, res)

        # this import need to be used after the app is created
        from rtools_gui.mainwindow import MainWindow
        mainwindow = MainWindow(conf, dbconn, dbprg_state, res)
        mainwindow.show()
        retval = app.exec_()

    exit(retval)
