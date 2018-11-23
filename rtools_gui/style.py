import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

GTK_CSS_FILE = os.path.join(os.path.dirname(__file__), "style.css")


def load():
    "Set our style for Gtk instance"
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(GTK_CSS_FILE)
    screen = Gdk.Screen.get_default()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
