import sys
import traceback
import logging
import logging.handlers
from gi.repository import Gtk


def log(message, *args, **kwargs):
    "Report simple message to log"
    logging.info(str(message), *args, **kwargs)


def fail_exit(message, exit_code=1):
    "Report message and exit with given exit_code"
    logging.critical(str(message))
    sys.exit(exit_code)


def ignored_exception():
    "Report ignored exception"
    logging.warning("Ignored exception", exc_info=True)


def setup_logging():
    "Setup logging functions"
    FORMAT = "rtools-gui %(levelname)s %(threadName)s: %(message)s"
    hdl = logging.handlers.SysLogHandler(address="/dev/log")
    hdl.setLevel(logging.INFO)
    hdl.setFormatter(logging.Formatter(FORMAT))
    logging.getLogger().addHandler(hdl)
    logging.getLogger().setLevel(logging.INFO)


def setup_stderr_logging():
    "Setup logging functions"
    FORMAT = "%(levelname)s %(threadName)s: %(message)s"
    hdl = logging.StreamHandler()
    hdl.setLevel(logging.INFO)
    hdl.setFormatter(logging.Formatter(FORMAT))
    logging.getLogger().addHandler(hdl)
    logging.getLogger().setLevel(logging.INFO)
