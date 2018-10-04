import io
import sys
import socket
from time import sleep
from threading import Thread, Event
from pexpect import fdpexpect
import ftdi1 as ftdi


class MoxTester:
    "Class controlling one specific mox tester."
    BOOT_MODE_SPI = 0b01
    BOOT_MODE_UART = 0b10

    def __init__(self, chip_id):
        ctx = ftdi.new()
        devs = ftdi.usb_find_all(ctx, 0x0403, 0x6011)
        # TODO handle no board connected
        # TODO use devs[1].next to found correct one with chip_id
        dev = devs[1].dev

        self.ctx = dict()
        # CN1 (detection, power supply and JTAG)
        self._a = _BitBangInterface(dev, ftdi.INTERFACE_A, 0x40)
        self.power(False)
        # CN2 (boot mode, hardware reset and SPI)
        self._b = _BitBangInterface(dev, ftdi.INTERFACE_B, 0xE0)
        self.reset(True)
        self.set_boot_mode(self.BOOT_MODE_SPI)
        # CN3 (Unused GPIO)
        self._c = _BitBangInterface(dev, ftdi.INTERFACE_C, 0x00)
        # CN4 (UART)
        self._d = _UARTInterface(dev, ftdi.INTERFACE_D)
        self._uart = None

    def power(self, enabled):
        "Set power state of board. In default power is disabled."
        self._a.set(not enabled, 0x40)

    def board_present(self):
        "Check if board is inserted"
        return not self._a.is_set(0x80)

    def power_supply_ok(self):
        "Check if 1.8V power supply is working / 1.8V is available"
        return not self._a.is_set(0x20)

    def set_boot_mode(self, mode):
        """Set boot mode of board. BOOT_MODE_SPI or BOOT_MODE_UART expected.
        In default BOOT_MODE_SPI is set."""
        if mode == self.BOOT_MODE_SPI:
            self._b.write(0x80, 0xC0)
        elif mode == self.BOOT_MODE_UART:
            self._b.write(0x40, 0xC0)
        else:
            raise MoxTesterInvalidMode(
                "Trying to set invalid mode: {}".format(mode))

    def reset(self, enabled):
        "Set hardware reset pin of board."
        self._b.set(not enabled, 0x20)

    def uart(self):
        "Returns fdpexpect object for comunication with UART"
        return self._d.pexpect()


def _common_interface_ctx(device, interface):
    ctx = ftdi.new()
    ftdi.set_interface(ctx, interface)
    ftdi.usb_open_dev(ctx, device)
    return ctx


class _BitBangInterface():
    "FTDI interface in Bit Bang mode"

    def __init__(self, device, interface, output_mask):
        self.ctx = _common_interface_ctx(device, interface)
        if ftdi.set_bitmode(self.ctx, output_mask, ftdi.BITMODE_BITBANG) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set bitbang mode for port: " + str(interface))

    def read(self, mask=0xFF):
        """Read status of pins. It returns read byte. You can use mask to
        automatically mask some bits. In default all bits are read and
        returned."""
        ret, value = ftdi.read_pins(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("Reading pins status failed")
        return int.from_bytes(value, 'big') & mask

    def write(self, data, mask=0xFF):
        "Write pins status. Whole byte at once."
        value = self.read(mask ^ 0xFF) | (data & mask)
        if ftdi.write_data(self.ctx, bytes([value])) < 0:
            raise MoxTesterCommunicationException("Write failed")

    def is_set(self, mask=0xFF):
        """Returns True if at least one of bits is set to 1. Mask can be used
        to limit considered bits."""
        return bool(self.read(mask))

    def set(self, is_set, mask=0xFF):
        """Sets given bits dependning on is_set boolean value. Bits can be
        selected by mask."""
        self.write(mask if is_set else 0x00, mask)


class _UARTInterface():
    "FTDI interface in Bit Bang mode"

    def __init__(self, device, interface):
        self.ctx = _common_interface_ctx(device, interface)
        if ftdi.set_bitmode(self.ctx, 0x00, ftdi.BITMODE_RESET) < 0:
            raise MoxTesterCommunicationException(
                "Unable to reset bitmode for port: " + str(interface))
        if ftdi.set_baudrate(self.ctx, 115200) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set baudrate for port:" + str(interface))
        if ftdi.usb_purge_rx_buffer(self.ctx) < 0:
            raise MoxTesterCommunicationException(
                "UART RX buffer purge failed for port: " + str(interface))

        self.socks = socket.socketpair()
        self.threadexit = Event()
        self.inputthread = Thread(target=self._input, daemon=True)
        self.inputthread.start()
        self.outputthread = Thread(target=self._output, daemon=True)
        self.outputthread.start()

    def __del__(self):
        self.threadexit.set()
        self.socks[0].close()
        self.socks[1].close()
        self.inputthread.join()
        self.outputthread.join()

    def _chunk_size(self):
        ret, chunk_size = ftdi.read_data_get_chunksize(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("UART get chunk size failed")
        return chunk_size

    def _input(self):
        chunk_size = self._chunk_size()
        # TODO corrent logging!
        with io.FileIO("moxtester.log", "w") as log:
            while not self.threadexit.is_set():
                ret, data = ftdi.read_data(self.ctx, chunk_size)
                if ret < 0:
                    raise MoxTesterCommunicationException("UART Read failed")
                elif ret > 0:
                    self.socks[0].sendall(data[0:ret])
                    log.write(data[0:ret])
                else:
                    # Sleep for short amount of time to not busyloop
                    sleep(0.01)

    def _output(self):
        chunk_size = self._chunk_size()
        while not self.threadexit.is_set():
            try:
                data = self.socks[0].recv(chunk_size)
            except ConnectionResetError:
                return
            if ftdi.write_data(self.ctx, data) < 0:
                raise MoxTesterCommunicationException("UART Write failed")

    def pexpect(self):
        "Returns fdpexpect handle."
        return fdpexpect.fdspawn(self.socks[1].fileno())


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


class MoxTesterAlreadyInUse(MoxTesterException):
    """Tester it self or port is already instantiated and should be closed
    before new one is opened."""
    pass
