import os
import math
from gi.repository import Gtk, Gdk
from . import db


class Window:
    "Grouper window"
    GLADE_FILE = os.path.join(os.path.dirname(__file__), "grouper.glade")
    BOARDS = {
        "A": "CPU",
        "B": "PCI",
        "C": "Topaz",
        "D": "SFP",
        "E": "Peridot",
        "F": "USB",
        "G": "PCI-passtrough",
    }
    FINAL = ["PLASTEV", "KRABICE"]

    def __init__(self, conf, db_connection, sets_variants):
        self.db_connection = db_connection
        self.sets_variants = sets_variants
        self.current_set_variant = None
        self.current_set = None
        self._set = dict()
        self.current_set_components = list()    
        self.current_mem = None
        self.loaded_mem = None
        self.board_number = 0
        self._builder = Gtk.Builder()
        self._builder.add_from_file(self.GLADE_FILE)
        self._builder.connect_signals(self)
        columns_count = 2
        sets_container = self._obj("GridSets")
        j = 0
        for set_name in self.sets_variants:
            button = Gtk.Button()
            button.set_label(set_name)
            button.connect("clicked", self.gtk_set_select, set_name)
            sets_container.attach(button, j%columns_count, math.floor(j/columns_count), 1, 1)
            j += 1
        window = self._obj("Window")
        window.show_all()
        window.fullscreen()

    def _obj(self, name):
        return self._builder.get_object(name)

    def gtk_set_select(self, _, set):
        "Generic set selector button click handler"
        self.current_set_components = list()
        self.loaded_mem = None
        # Excpected 'A' module is first
        # because of memory check
        for comp in self.sets_variants[set]:
            if isinstance(comp, dict):
                board_type = next(iter(comp))
                self.loaded_mem = comp[board_type]
            else:
                board_type = comp
            self.current_set_components.append(board_type)
        self.current_set_components.extend(self.FINAL)
        self._obj("MainStack").set_visible_child(self._obj("SetsGrouper"))
        self._obj("ScancodeEntry").grab_focus()
        self._wipe_set()
        self.current_set_variant = set
        self.current_set = {board: None for board in self.current_set_components}
        for board in self.current_set_components:
            self._new_set_board(board)
        self._obj("SetGrid").show_all()
        self.gtk_info_text("Začněte naskenováním první desky")

    def _new_set_board(self, board):
        icon = Gtk.Image()
        label = Gtk.Label()
        label.set_text("{} ({})".format(board, self.BOARDS.get(board, "unknown")))
        label.set_halign(Gtk.Align.START)
        grid = self._obj("SetGrid")
        row = len(self._set)
        grid.attach(icon, 1, row, 1, 1)
        grid.attach(label, 2, row, 1, 1)
        self._set[board] = {
            "icon": icon,
            "label": label,
        }
        self.gtk_set_update(board)

    def _wipe_set(self):
        grid = self._obj("SetGrid")
        for _, wset in self._set.items():
            grid.remove(wset['icon'])
            grid.remove(wset['label'])
        self._set = dict()

    def gtk_back_to_selector(self, _):
        "Button click handler for back button"
        self._obj("MainStack").set_visible_child(self._obj("SetsSelector"))

    def gtk_set_update(self, board):
        "Update board presence in list."
        self._set[board]['icon'].set_from_stock(
            Gtk.STOCK_DELETE if self.current_set[board] is None else Gtk.STOCK_OK,
            Gtk.IconSize.LARGE_TOOLBAR)

    def gtk_info_text(self, message, style="info"):
        label = self._obj("InfoLabel")
        label.set_text(message)
        style_ctx = label.get_style_context()
        for sclass in style_ctx.list_classes():
            if sclass.startswith("label-"):
                style_ctx.remove_class(sclass)
        style_ctx.add_class("label-" + style)

    def gtk_bardcode_entry(self, _):
        "Handler called when text is entered in field"
        entry = self._obj("ScancodeEntry")
        serial_text = entry.get_text()
        entry.set_text("")
        try:
            serial_number = int(serial_text)
        except ValueError:
            self.gtk_info_text("Hodnota nebyla číslo. Byla použita čtečka?", "error")
            return
        try:
            board = db.Board(self.db_connection, serial_number)
        except db.DBException:
            self.gtk_info_text("Tato deska není v databázi. Byl naskenován skutečně štítek z Turrisu?", "error")
            return
        if board.type not in self.current_set:
            self.gtk_info_text("Tato deska ({}) není v aktuální sestavě!".format(board.type), "error")
            return
        if self.current_set[board.type] is not None:
            if self.board_number < len(self.current_set_components) - len(self.FINAL):
                if self.current_set[board.type].serial_number == serial_number:
                    self.gtk_info_text("Tato deska ({}) již byla přidána!".format(board.type), "warning")
                    return
        if db.Set.included(self.db_connection, serial_number):
            self.gtk_info_text("Tato deska ({}) je již součástí jiné sestavy!".format(board.type), "error")
            return
        if not board.last_run_result():
            self.gtk_info_text("Poslední zaznamenaný test pro tuto desku neprošel!", "error")
            return
        if board.type != self.current_set_components[self.board_number] and self.current_set_components[self.board_number] not in self.FINAL:
            self.gtk_info_text("Deska {0}: špatné pořadí očekávána {1}".format(board.type, self.current_set_components[self.board_number]))
            return
        # memory check on first board in set
        if board.type == self.current_set_components[0]:
            self.current_mem = board.core_info().get('mem')
            if self.current_mem is None:
                self.gtk_info_text("Tato deska ({0}) nemá záznam o paměti".format(board.type))
                return
            if not self.current_mem == self.loaded_mem:
                self.gtk_info_text("Paměť desky ({0}) neodpovídá předpisům".format(board.type))
                return
        if self.current_set_components[self.board_number] in self.FINAL:
            self.current_set[self.current_set_components[self.board_number]] = 1
            self.gtk_info_text("{0} potvrzeno".format(self.current_set_components[self.board_number]))
            self.gtk_set_update(self.current_set_components[self.board_number])
        else:
            self.current_set[board.type] = board
            self.gtk_info_text("Deska ({}) byla přidána.".format(board.type))
            self.gtk_set_update(board.type)
        # Check if this is last one
        self.board_number += 1
        if self.board_number < len(self.current_set_components):
            return
        # Add it to database
        dbset = db.Set(self.db_connection, self.current_set_variant)
        for types, board in self.current_set.items():
            if types not in self.FINAL:
                dbset.add_board(board)
        # Continue with full set
        self.gtk_info_text("Sestava sestavena.", "ok")
        self.board_number = 0
        # Reset current set
        for board in self.current_set:
            self.current_set[board] = None
            self.gtk_set_update(board)
            
    def gtks_on_delete_event(self, *args):
        Gtk.main_quit(*args)
