import sys
import traceback
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Rsvg', '2.0')
gi.require_foreign("cairo")
from gi.repository import Gtk, Gdk
from . import guard, resources, db
from . import mainwindow, style
from .conf import Configs


def _printException(type, value, tb):
    type = "%s.%s" % (type.__module__, type.__name__)
    trace = "\n".join(traceback.format_tb(tb))
    print(
        "Exception occured:\n%s(\"%s\")\nTraceback:\n%s" % (type, value, trace))
    print("Error occured. Exiting...")
    sys.exit(1)


def main():
    "Main function of rtools-gui"
    argv = Gtk.init(sys.argv[1:])
    conf = Configs(argv)
    # TODO setup logging

    with guard.Guard(conf):
        # Database and resources
        res = resources.Resources(conf)
        dbconn = db.connect(conf)
        dbprg_state = db.ProgrammerState(dbconn, res)

        # Graphics
        style.load()
        mainwindow.MainWindow(conf, dbconn, dbprg_state, res)
        Gtk.main()
