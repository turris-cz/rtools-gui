import os
import traceback
from gi.repository import GLib, Gtk
from . import report
from .moxtester import MoxTester
from .moxtester.exceptions import MoxTesterException
from .workflow import WorkFlow, WorkFlowHandler
from .svgimage import SVGImage


class Programmer(WorkFlowHandler):
    "Programmer widget"
    _IMG_PREFIX = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'img')
    _STATE_TO_PIX = {
        WorkFlow.STEP_UNKNOWN:
            os.path.join(_IMG_PREFIX, "icons/unknown.png"),
        WorkFlow.STEP_RUNNING:
            os.path.join(_IMG_PREFIX, "../img/icons/run.png"),
        WorkFlow.STEP_FAILED:
            os.path.join(_IMG_PREFIX, "../img/icons/fail.png"),
        WorkFlow.STEP_OK:
            os.path.join(_IMG_PREFIX, "../img/icons/ok.png"),
        WorkFlow.STEP_UNSTABLE:
            os.path.join(_IMG_PREFIX, "../img/icons/unstable.png"),
    }
    GLADE_FILE = os.path.join(os.path.dirname(__file__), "programmer.glade")

    def __init__(self, main_window, conf, db_connection, db_programmer_state,
                 resources, index):
        self.main_window = main_window
        self.conf = conf
        self.db_connection = db_connection
        self.db_programmer_state = db_programmer_state
        self.resources = resources
        self.index = index
        self._steps = dict()
        self._progress_step_value = None  # Se note in progress_step
        self.fail_count = 0

        self._builder = Gtk.Builder()
        self._builder.add_from_file(self.GLADE_FILE)
        self._builder.connect_signals(self)

        self.widget = self._obj("ProgrammerFrame")
        self._obj("ProgrammerLabel").set_label(
            'Programátor ' + str(index + 1))
        self._obj('IntroImage').add(
            SVGImage(os.path.join(self._IMG_PREFIX, "logo.svg")))
        self.widget.show_all()

        self.workflow = None  # Current workflow for this programmer
        self.programmer = None  # Handle for MoxTester
        self.gtk_connect_programmer()

    def _obj(self, name):
        return self._builder.get_object(name)

    def gtk_intro_error(self, message):
        "Display error for intro page."
        label = self._obj("IntroErrorLabel")
        self._obj("IntroStack").set_visible_child(label)
        label.set_text(str(message))

    def gtk_select(self):
        """Try to select this programmer for new board session.
        Returns error string or None if selection was ok.
        """
        if self.programmer is None:
            self.gtk_connect_programmer()  # First try to connect it
            if self.programmer is None:
                return "Programátor {} zřejmě není připojen".format(self.index + 1)
        if self.workflow is not None:
            return "Programátor {} je aktuálně obsazen".format(self.index + 1)
        self.programmer.reset_tester()
        if not self.programmer.board_present():
            return "Do programátoru {} není vložená deska".format(self.index + 1)
        self._obj('ContentStack').set_visible_child(self._obj('ContentIntro'))
        self._obj('IntroStack').set_visible_child(self._obj('IntroScanCode'))
        self._obj('BarcodeEntry').grab_focus()
        return None

    def gtk_connect_programmer(self):
        "Try to connect programmer"
        try:
            self.programmer = MoxTester(self.index)
            self.programmer.selftest()
        except MoxTesterException:
            report.error(
                "Programmer connection failed: " + str(traceback.format_exc()))
            # Ok this failed so we don't have programmer
            self.programmer = None
        if self.programmer is not None:
            stack = self._obj("IntroStack")
            stack.set_visible_child(self._obj("IntroPrepared"))

    def gtks_barcode_entry(self, *udata):
        """Slot called when barcode is scanned to input box. Should check if
        given code is valid and start flashing process"""
        del udata
        entry = self._obj("BarcodeEntry")
        serial_text = entry.get_text()
        entry.set_text("")
        try:
            serial_number = int(serial_text)
        except ValueError:
            self.gtk_intro_error("Hodnota nebyla číslo. Byla použita čtečka?")
            return
        self.main_window.gtk_focus()
        if (serial_number >> 32) == 0xFFFFFFFF:
            self.gtk_intro_error("Naskenován kód programátoru")
            return
        try:
            self.workflow = WorkFlow(
                self, self.conf, self.db_connection, self.db_programmer_state,
                self.resources, self.programmer, serial_number)
        except Exception as e:
            report.error(
                "Workflow creation failed:" + str(traceback.format_exc()))
            # TODO log this exception!
            self.workflow = None
            self.gtk_intro_error(str(e))
            return
        self._obj("IntroStack").set_visible_child(
            self._obj("IntroPrepared"))

        # Update GUI
        self._obj("ContentStack").set_visible_child(self._obj("ContentWork"))
        self._obj("TypeLabel").set_text(self.workflow.get_board_name())
        self._obj("SerialNumberLabel").set_text(hex(serial_number))
        self._obj("WorkStack").set_visible_child(self._obj("WorkProgress"))
        self._wipe_steps()
        for step in self.workflow.get_steps():
            self._new_step(step)
        self._obj("WorkStepsGrid").show_all()
        run_progress = self._obj("RunProgress")
        run_progress.set_max_value(len(self._steps))
        run_progress.set_value(0)

        self.workflow.start()  # And lastly start worklow

    def _wipe_steps(self):
        grid = self._obj("WorkStepsGrid")
        for id, step in self._steps.items():
            grid.remove(step['icon'])
            grid.remove(step['label'])
        self._steps = dict()

    def _new_step(self, step):
        icon = Gtk.Image()
        label = Gtk.Label()
        label.set_text(step['name'])
        label.set_halign(Gtk.Align.START)
        grid = self._obj("WorkStepsGrid")
        row = len(self._steps)
        grid.attach(icon, 1, row, 1, 1)
        grid.attach(label, 2, row, 1, 1)
        self._steps[step['id']] = {
            "icon": icon,
            "label": label,
        }
        self.gtk_step_update(step['id'], step['state'])

    def gtk_step_update(self, step_id, state):
        """Set state of one of steps. state is string and can be one of
        supported steps from workflow.
        """
        img_path = self._STATE_TO_PIX[state]
        icon = self._steps[step_id]['icon']
        if os.path.isfile(img_path):
            icon.set_from_file(img_path)
        else:
            icon.set_from_stock(Gtk.STOCK_MISSING_IMAGE)

    def _gtk_progress_step(self):
        value = self._progress_step_value
        self._progress_step_value = None
        self._obj('StepProgress').set_fraction(value)

    def progress_step(self, value):
        # Note: There is a problem that flashing produces a lot of calls to
        # this function. For some reason a lot of idle tasks freezes GUI so
        # instead of generating new task for every single call we generate only
        # one untill that one is executed. This implementation of course is not
        # exactly safe and there is race condition where possible update is
        # dropped but we just don't care. Sorry to anyone who cares.
        spawn = self._progress_step_value is None
        self._progress_step_value = value
        if spawn:
            GLib.idle_add(self._gtk_progress_step)

    def _gtk_step_update(self, step_id, state):
        self.gtk_step_update(step_id, state)
        if state == WorkFlow.STEP_FAILED or state == WorkFlow.STEP_OK:
            run_progress = self._obj("RunProgress")
            run_progress.set_value(run_progress.get_value() + 1)

    def step_update(self, step_id, state):
        GLib.idle_add(self._gtk_step_update, step_id, state)

    def _gtk_workflow_exit(self, error):
        # TODO if error is about disconnected programmer then we should reset
        # our self and go to screen about disconnected programmer.
        if not error:
            self._obj("WorkStack").set_visible_child(self._obj("WorkDone"))
            self.fail_count = 0
        else:
            self._obj("WorkStack").set_visible_child(self._obj('WorkError'))
            self._obj("WorkErrorLabel").set_text(error)
            self.fail_count = self.fail_count + 1
        self._obj('StationTestLabel').set_visible(
            self.conf.suggest_test > 0 and self.fail_count >= self.conf.suggest_test)

    def workflow_exit(self, error=None):
        self.workflow = None
        GLib.idle_add(self._gtk_workflow_exit, error)
