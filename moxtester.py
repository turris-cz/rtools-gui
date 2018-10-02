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
    CONF = {
        "A": {
            "interface": ftdi.INTERFACE_A,
            "mode": ftdi.BITMODE_BITBANG,
            "output_mask": 0x40
        },
        "B": {
            "interface": ftdi.INTERFACE_B,
            "mode": ftdi.BITMODE_BITBANG,
            "output_mask": 0xE0
        },
        "C": {
            "interface": ftdi.INTERFACE_C,
            "mode": ftdi.BITMODE_BITBANG,
            "output_mask": 0x00
        },
        "D": {
            "interface": ftdi.INTERFACE_D,
            "mode": ftdi.BITMODE_RESET,
            "output_mask": 0x00
        }
    }

    def __init_ctx__(self, dev, port_id):
        self.ctx[port_id] = ftdi.new()
        ftdi.set_interface(self.ctx[port_id], self.CONF[port_id]["interface"])
        ftdi.usb_open_dev(self.ctx[port_id], dev)
        if ftdi.set_bitmode(
                self.ctx[port_id], self.CONF[port_id]["output_mask"],
                self.CONF[port_id]["mode"]) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set mode for port " + port_id)

    def __init__(self, chip_id):
        ctx = ftdi.new()
        devs = ftdi.usb_find_all(ctx, 0x0403, 0x6011)
        # TODO handle no board connected
        # TODO use devs[1].next to found correct one with chip_id
        dev = devs[1].dev

        self.ctx = dict()
        # CN1 (detection, power supply and JTAG)
        self.__init_ctx__(dev, "A")
        self.power(False)
        # CN2 (boot mode, hardware reset and SPI)
        self.__init_ctx__(dev, "B")
        self.set_boot_mode(self.BOOT_MODE_SPI)
        # CN3 (Unused GPIO)
        self.__init_ctx__(dev, "C")
        # CN4 (UART)
        self.__init_ctx__(dev, "D")
        if ftdi.set_baudrate(self.ctx["D"], 115200) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set baudrate for D port")
        self._uart = None

    def _read_pins(self, port):
        ret, value = ftdi.read_pins(self.ctx[port])
        if ret < 0:
            raise MoxTesterCommunicationException("Reading pins status failed")
        return int.from_bytes(value, 'big')

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
        "Set power state of board. In default power is disabled."
        self._write_bits("A", 0x40, not enabled)

    def board_present(self):
        "Check if board is inserted"
        return not self._read_bits("A", 0x80)

    def power_supply_ok(self):
        "Check if 1.8V power supply is working / 1.8V is available"
        return not self._read_bits("A", 0x20)

    def set_boot_mode(self, mode):
        """Set boot mode of board. BOOT_MODE_SPI or BOOT_MODE_UART expected.
        In default BOOT_MODE_SPI is set."""
        if mode == self.BOOT_MODE_SPI:
            self._write("B", 0xC0, 0x80)
        elif mode == self.BOOT_MODE_UART:
            self._write("B", 0xC0, 0x40)
        else:
            raise MoxTesterInvalidMode(
                "Trying to set invalid mode: {}".format(mode))

    def reset(self, enabled):
        "Set hardware reset pin of board."
        self._write_bits("B", 0x20, enabled)

    def uart(self):
        "Returns fdpexpect object for comunication with UART"
        return MoxTesterUART(self)


class MoxTesterUART(fdpexpect.fdspawn):
    "UART access for Mox Tester."

    def __init__(self, moxtester):
        if moxtester._uart is not None:
            raise MoxTesterAlreadyInUse("UART port is already in use.")
        self.moxtester = moxtester
        moxtester._uart = self
        self.ctx = moxtester.ctx["D"]
        if ftdi.usb_purge_rx_buffer(self.ctx) < 0:
            raise MoxTesterCommunicationException(
                "UART RX buffer purge failed.")

        self.socks = socket.socketpair()
        self.threadexit = Event()
        self.inputthread = Thread(target=self._input, daemon=True)
        self.inputthread.start()
        self.outputthread = Thread(target=self._output, daemon=True)
        self.outputthread.start()
        super().__init__(self.socks[1].fileno())

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, tp, value, traceback):
        self.close()

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

    def close(self):
        "Close UART connection"
        if self.moxtester is None:
            return
        self.moxtester._uart = None
        self.moxtester = None
        self.threadexit.set()
        self.socks[0].close()
        self.socks[1].close()
        self.inputthread.join()
        self.outputthread.join()


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
