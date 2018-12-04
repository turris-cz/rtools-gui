import sys
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Rsvg', '2.0')
gi.require_foreign("cairo")
from gi.repository import Gtk, Gdk
from . import guard, resources, db, report
from . import mainwindow, style
from .conf import Configs


def main():
    "Main function of rtools-gui"
    argv = Gtk.init(sys.argv[1:])
    conf = Configs(argv)
    report.setup_logging()
    sys.excepthook = report.report_uncaught_exception_gtk

    with guard.Guard(conf):
        # Database and resources
        res = resources.Resources(conf)
        dbconn = db.connect(conf)
        dbprg_state = db.ProgrammerState(dbconn, res)

        # Graphics
        style.load()
        mainwindow.MainWindow(conf, dbconn, dbprg_state, res)
        Gtk.main()
