from gi.repository import Gtk, Rsvg


class SVGImage(Gtk.DrawingArea):
    "Auto filling resizable SVG image"

    def __init__(self, file):
        self._scale = 1
        super().__init__()
        self._svg_h = Rsvg.Handle.new_from_file(file)
        self._dimensions = self._svg_h.get_dimensions()

    def do_size_allocate(self, allocate):
        "size-allocate handler"
        xscale = allocate.width / self._dimensions.width
        yscale = allocate.height / self._dimensions.height
        self._scale = min(xscale, yscale)
        allocate.width = int(self._dimensions.width * self._scale)
        allocate.height = int(self._dimensions.height * self._scale)
        Gtk.DrawingArea.do_size_allocate(self, allocate)

    def do_draw(self, cr):
        "Draw handler"
        cr.scale(self._scale, self._scale)
        self._svg_h.render_cairo(cr)
