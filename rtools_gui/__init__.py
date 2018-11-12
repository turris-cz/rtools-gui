import sys
import traceback
from PyQt5.QtWidgets import QApplication
from . import guard, resources, db


def _printException(type, value, tb):
    type = "%s.%s" % (type.__module__, type.__name__)
    trace = "\n".join(traceback.format_tb(tb))
    print(
        "Exception occured:\n%s(\"%s\")\nTraceback:\n%s" % (type, value, trace))
    print("Error occured. Exiting...")
    sys.exit(1)


def main(argv):
    with guard.Guard():
        app = QApplication(argv)

        # Load all resources
        res = resources.Resources()

        # this import need to be used after the app is created
        from rtools_gui.mainwindow import MainWindow
        mainwindow = MainWindow(dbconn, res)
        mainwindow.show()
        retval = app.exec_()

    exit(retval)
