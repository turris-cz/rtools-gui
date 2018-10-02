import socket
from pexpect import fdpexpect
import ftdi1 as ftdi


class MoxTester:
    "Class controlling one specific mox tester."
    BOOT_MODE_SPI = 0b01
    BOOT_MODE_UART = 0b10

    def __init__(self, chip_id):
        ctx = ftdi.new()
        devs = ftdi.usb_find_all(ctx, 0x0403, 0x6011)
        # TODO use devs[1].next to found correct one with chip_id
        dev = devs[1].dev

        self.ctx = dict()
        ## CN1 (detection, power supply and JTAG) ##
        self.ctx["A"] = ftdi.new()
        ftdi.set_interface(self.ctx["A"], ftdi.INTERFACE_A)
        ftdi.usb_open_dev(self.ctx["A"], dev)
        if ftdi.set_bitmode(self.ctx["A"], 0x40, ftdi.BITMODE_BITBANG) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set mode for port A")
        self.power(False)  # Set power supply do disable
        ## CN2 (boot mode, hardware reset and SPI) ##
        self.ctx["B"] = ftdi.new()
        ftdi.set_interface(self.ctx["B"], ftdi.INTERFACE_B)
        ftdi.usb_open_dev(self.ctx["B"], dev)
        # TODO probably also missmasking SPI
        if ftdi.set_bitmode(self.ctx["B"], 0xE0, ftdi.BITMODE_BITBANG) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set mode for port B")
        ## CN3 (Unused GPIO) ##
        # skipped for now
        ## CN4 (UART) ##
        return
        self.ctx["D"] = ftdi.new()
        ftdi.set_interface(self.ctx["D"], ftdi.INTERFACE_D)
        ftdi.usb_open_dev(self.ctx["D"], dev)
        if ftdi.set_bitmode(self.ctx["D"], 0x00, ftdi.BITMODE_RESET) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set mode for port D")
        self.uart = None

    def _read_pins(self, port):
        return int.from_bytes(ftdi.read_pins(self.ctx[port])[1], 'big')

    def _write(self, port, mask, data):
        "Write given data according to given mask"
        value = (self._read_pins(port) & (mask ^ 0xFF)) | (mask & data)
        if ftdi.write_data(self.ctx[port], bytes([value])) < 0:
            raise MoxTesterCommunicationException("Write failed")

    def _write_bits(self, port, mask, bit_value):
        "Write bits of given mask to 1 or 0 given by boolean bit_value."
        self. _write(port, mask, mask if bit_value else 0x00)

    def _read(self, port, mask):
        "Reads single byte (int) masked with given mask."
        return self._read_pins(port) & mask

    def _read_bits(self, port, mask):
        """Read bits of given mask and returns True if at least one of them is
        set."""
        return bool(self._read(port, mask))

    def power(self, enabled):
        "Set power state of board"
        self._write_bits("A", 0x40, not enabled)

    def board_present(self):
        "Check if board is inserted"
        return not self._read_bits("A", 0x80)

    def power_supply_ok(self):
        "Check if 1.8V power supply is working / 1.8V is available"
        return not self._read_bits("A", 0x20)

    def set_boot_mode(self, mode):
        "Set boot mode of board. BOOT_MODE_SPI or BOOT_MODE_UART expected."
        if mode == self.BOOT_MODE_SPI:
            self._write("B", 0xC0, 0x40)
        elif mode == self.BOOT_MODE_UART:
            self._write("B", 0xC0, 0x80)
        else:
            raise MoxTesterInvalidMode(
                "Trying to set invalid mode: {}".format(mode))

    def reset(self, enabled):
        "Set hardware reset pin of board."
        self._write_bits("B", 0x20, enabled)

    def open_uart(self):
        "Returns File object for comunication with UART"
        return MoxTesterUART(self)


class MoxTesterUART(fdpexpect.fdspawn):
    "UART access for Mox Tester."

    def __init__(self, moxtester):
        self.moxtester = moxtester
        moxtester.uart = self

        self.socks = socket.socketpair()
        super().__init__(self.socks[1].fileno())
        # TODO


class MoxTesterException(Exception):
    """Generic exception raised from MoxTester class."""
    pass


class MoxTesterCommunicationException(MoxTesterException):
    """Exception raised by MoxTester when problem is encountered durring tester
    communication."""
    pass


class MoxTesterInvalidMode(MoxTesterException):
    """Trying to set invalid mode."""
    pass
