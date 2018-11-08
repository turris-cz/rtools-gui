import importlib
import logging
import os
import sys
import errno
import traceback
from PyQt5.QtWidgets import QApplication
from . import resources


def _printException(type, value, tb):
    type = "%s.%s" % (type.__module__, type.__name__)
    trace = "\n".join(traceback.format_tb(tb))
    print(
        "Exception occured:\n%s(\"%s\")\nTraceback:\n%s" % (type, value, trace))
    print("Error occured. Exiting...")
    sys.exit(1)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        # This line will enable to handle exceptions outside of Qt event loop
        sys.excepthook = _printException

        # Load all resources
        resources.load_resources()
