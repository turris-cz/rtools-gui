import os
from gi.repository import Gtk, Gdk
from .custom_exceptions import DbError, IncorrectSerialNumber
from .programmer import Programmer


class MainWindow:
    "Main window of application"
    GLADE_FILE = os.path.join(os.path.dirname(__file__), "mainwindow.glade")

    def __init__(self, conf, db_connection, db_programmer_state, resources):
        self.conf = conf

        self._builder = Gtk.Builder()
        self._builder.add_from_file(self.GLADE_FILE)
        self._builder.connect_signals(self)

        self.window = self._builder.get_object("MainWindow")
        self.window.show_all()
        self.window.fullscreen()
        self.gtk_display_msg(None)

        prg_grid = self._builder.get_object('ProgrammerGrid')
        # Create programmers
        self.programmers = [None]*4
        for i in range(4):
            prg = Programmer(self, conf, db_connection, db_programmer_state,
                             resources, i)
            prg_grid.attach(prg.widget, i % 2, i // 2, 1, 1)
            self.programmers[i] = prg

    def gtks_on_delete_event(self, *args):
        Gtk.main_quit(*args)

    def gtk_focus(self):
        "Set focus back to primary window input box."
        self._builder.get_object("BarcodeEntry").grab_focus()

    def gtk_display_msg(self, message):
        """"Display given message in main window message box. You can pass None
        as a message to clear error box."""
        label = self._builder.get_object('ErrorLabel')
        if message is None:
            label.hide()
        else:
            label.show()
            label.set_label(message)

    def gtks_barcode_scan(self, *udata):
        "Called when text is entered to primary text field in main window"
        del udata
        self.gtk_display_msg(None)
        entry = self._builder.get_object('BarcodeEntry')
        text = entry.get_text()
        entry.set_text("")
        try:
            serial_number = int(text)
        except ValueError:
            self.gtk_display_msg("Hodnota nebyla číslo. Byla použita čtečka?")
            return
        index = serial_number & 0xFFFFFFFF
        if (serial_number >> 32) != 0xFFFFFFFF or index < 0 or index > 3:
            self.gtk_display_msg(
                "Naskenovaný kód není validní pro volbu programátoru")
            return
        msg = self.programmers[index].gtk_select()
        if msg is not None:
            self.gtk_display_msg(msg)
