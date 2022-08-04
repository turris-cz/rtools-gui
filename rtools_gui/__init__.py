import os
import sys
import yaml
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Rsvg', '2.0')
gi.require_foreign("cairo")
from gi.repository import Gtk, Gdk
from . import guard, resources, db, report
from . import mainwindow, style
from . import grouper
from .conf import Configs


def _common_main(prepare):
    "Main structure for both main() and grouper_main()"
    argv = Gtk.init(sys.argv[1:])
    conf = Configs(argv)

    if os.environ.get("RTOOLS_STDERR") == "1":
        report.setup_stderr_logging()
    else:
        report.setup_logging()

    with guard.Guard(conf):
        dbconn = db.connect(conf)
        style.load()
        prepare(conf, dbconn)
        Gtk.main()


def _rtools_gui(conf, dbconn):
    # Resources and programmer state
    res = resources.Resources(conf)
    dbprg_state = db.ProgrammerState(dbconn, res)
    # Graphics
    mainwindow.MainWindow(conf, dbconn, dbprg_state, res)


def rtools_gui_main():
    "Main function of rtools-gui"
    _common_main(_rtools_gui)


def _rtools_gui_grouper(conf, dbconn):
    # Load available sets
    with open(os.path.join(os.path.dirname(__file__), "..", "grouper_sets.yml"), 'r') as file:
        sets_variants = yaml.safe_load(file)
    # Graphics
    grouper.Window(conf, dbconn, sets_variants)


def rtools_gui_grouper_main():
    "Main function of rtools-gui-grouper"
    _common_main(_rtools_gui_grouper)
