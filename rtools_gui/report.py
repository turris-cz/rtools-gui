import sys
import traceback
import logging
import logging.handlers
from gi.repository import Gtk


def log(message):
    "Report simple message to log"
    logging.info(str(message))


def fail_exit(message, exit_code=1):
    "Report message and exit with given exit_code"
    logging.critical(str(message))
    sys.exit(exit_code)


def error(message):
    "Print error message"
    logging.error(str(message))


def ignored_exception():
    "Report ignored exception"
    logging.warning("Ignored exception: " + str(traceback.format_exc()))


def report_uncaught_exception_gtk(tp, value, tb):
    "Exception handler for all uncaught exceptions"
    msg = "Uncaught exception: {}.{}({})\nTraceback:\n{}".format(
        tp.__module__, tp.__name__, value, "\n".join(traceback.format_tb(tb)))
    logging.error(msg)
    message_dialog = Gtk.MessageDialog(
        None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
        Gtk.ButtonsType.CLOSE, msg)
    message_dialog.run()
    sys.exit(9)


def setup_logging():
    "Setup logging functions"
    FORMAT = "rtools-gui %(levelname)s %(threadName)s: %(message)s"
    hdl = logging.handlers.SysLogHandler(address='/dev/log')
    hdl.setLevel(logging.INFO)
    hdl.setFormatter(logging.Formatter(FORMAT))
    logging.getLogger().addHandler(hdl)
    logging.getLogger().setLevel(logging.INFO)
