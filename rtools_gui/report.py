import sys
import traceback
from gi.repository import Gtk


def fail_exit(message, exit_code=1):
    "Report message and exit with given exit_code"
    print("Fatal: " + str(message), file=sys.stderr)
    sys.exit(exit_code)


def error(message):
    "Print error message"
    print("Error: " + str(message), file=sys.stderr)


def report_uncaught_exception_gtk(tp, value, tb):
    "Exception handler for all uncaught exceptions"
    msg = "Uncaught exception: {}.{}({})\nTraceback:\n{}".format(
        tp.__module__, tp.__name__, value, "\n".join(traceback.format_tb(tb)))
    print(msg, file=sys.stderr)
    message_dialog = Gtk.MessageDialog(
        None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
        Gtk.ButtonsType.CLOSE, msg)
    message_dialog.run()
    sys.exit(9)
