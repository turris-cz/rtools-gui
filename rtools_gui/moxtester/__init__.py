import os
import sys
import io
import socket
from time import sleep
from threading import Thread, Event
from pexpect import fdpexpect
import ftdi1 as ftdi
from .. import report
from .spiflash import SPIFlash
from .moximager import MoxImager
from .exceptions import MoxTesterException
from .exceptions import MoxTesterNotFoundException
from .exceptions import MoxTesterCommunicationException
from .exceptions import MoxTesterInvalidMode
from .exceptions import MoxTesterSPIException
from .exceptions import MoxTesterSPITestFail


class MoxTester:
    "Class controlling one specific mox tester."
    BOOT_MODE_SPI = 0b01
    BOOT_MODE_UART = 0b10

    def __init__(self, tester_id):
        self.tester_id = tester_id
        self.board_id = "unknown"

        self.ctx = ftdi.new()
        ret, devs = ftdi.usb_find_all(self.ctx, 0x0403, 0x6011)
        if ret < 0:
            raise MoxTesterCommunicationException("Unable to list USB devices")
        self.dev = None
        while self.dev is None and devs is not None:
            # Ignore any device that fails open (those are in use)
            if ftdi.usb_open_dev(self.ctx, devs.dev) == 0:
                if ftdi.read_eeprom(self.ctx) < 0:
                    raise MoxTesterCommunicationException("EEPROM read failed")
                if ftdi.eeprom_decode(self.ctx, 0) < 0:
                    raise MoxTesterCommunicationException(
                        'EEPROM decode failed')
                ret, chip_tp = ftdi.get_eeprom_value(self.ctx, ftdi.CHIP_TYPE)
                if ret < 0:
                    raise MoxTesterCommunicationException(
                        "Reading chip type (id) failed")
                if chip_tp == tester_id:
                    self.dev = devs.dev  # Setting dev if correct device found
                if ftdi.usb_reset(self.ctx) != 0:
                    raise MoxTesterCommunicationException(
                        "FTDI USB device reset failed")
                if ftdi.usb_close(self.ctx) != 0:
                    raise MoxTesterCommunicationException(
                        "FTDI USB device close failed")
            devs = devs.next
        if self.dev is None:
            raise MoxTesterNotFoundException(
                "There is no connected tester with id: " + str(tester_id))
        self._a = None
        self._b = None
        self._c = None
        self._d = None
        self.connect_tester()

    def disconnect_tester(self):
        """Disconnect this object from tester"""
        self._a.__del__()
        self._a = None
        self._b.__del__()
        self._b = None
        self._c.__del__()
        self._c = None
        self._d.__del__()
        self._d = None

    def connect_tester(self):
        """Restart FTDI device and connect to tester"""
        if self._a is not None or self._b is not None or self._c is not None \
                or self._d is not None:
            raise MoxTesterException("Trying to connect to already connected tester")
        # Connect
        self._a = _BitBangInterface(self.dev, ftdi.INTERFACE_A, 0x40)
        self._b = _SPIInterface(self.dev, ftdi.INTERFACE_B, 0xE0)
        self._c = _BitBangInterface(self.dev, ftdi.INTERFACE_C, 0x00)
        # TODO propagate configuration to log here
        self._d = _UARTInterface(self.dev, ftdi.INTERFACE_D, self.board_id)
        self.default()

    def reset_tester(self):
        """ReseteMoxTester device. It disconnects MoxTester from FTDI USB
        device, restarts it and reconnects."""
        self.disconnect_tester()
        # Reset
        if ftdi.usb_open_dev(self.ctx, self.dev) != 0:
            raise MoxTesterCommunicationException(
                "Unable to open FTDI interface for reset")
        if ftdi.usb_reset(self.ctx) != 0:
            raise MoxTesterCommunicationException(
                "Unable to reset FTDI USB device")
        if ftdi.usb_close(self.ctx) != 0:
            raise MoxTesterCommunicationException(
                "Closing USB FTDI device failed")
        self.connect_tester()
    
    def set_board_id(self, board_id="unknown"):
        """Set identifier for board"""
        self.board_id = board_id
        self._d.set_board_id(board_id)

    def default(self):
        """Return tester state to default"""
        self.power(False)
        self.reset(True)
        self.set_boot_mode(self.BOOT_MODE_SPI)

    def selftest(self):
        "Runs various self-test operations (such as SPI loopback test)"
        self._b.spi_selftest()

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
        In default BOOT_MODE_SPI is set.

        NOTE: On current Mox Tester this does not work!
        """
        # TODO lower bit is negated here because of hardware change on board
        # durring development. Fix this to be consistent with final board.
        if mode == self.BOOT_MODE_SPI:
            self._b.gpio_set(0x80, 0xC0)
        elif mode == self.BOOT_MODE_UART:
            self._b.gpio_set(0x40, 0xC0)
        else:
            raise MoxTesterInvalidMode(
                "Trying to set invalid mode: {}".format(mode))

    def reset(self, enabled):
        "Set hardware reset pin of board."
        self._b.set(enabled, 0x20)

    def uart_fileno(self):
        "Returns fileno for comunication with UART"
        return self._d.fileno()

    def uart(self):
        "Returns fdpexpect object for comunication with UART"
        return self._d.pexpect()

    def mox_imager(self, resources):
        """Returns instance of MoxImager for OTP flashing."""
        return MoxImager(self, resources)

    def spiflash(self):
        """Return instance of SPIFlash to control flash.
        Object returned from this function has to be used with 'with'
        statement. Note that entering 'with' statement automatically power ups
        board, sets it to reset state, configures needed pins as output and
        sets boot mode to UART.
        On 'with' statement left it powers down device, sets boot mode to SPI
        and configures all SPI pins as input. Note that device is left in reset
        state.
        """
        return SPIFlash(self, self._b)


class _Interface:
    "Common FTDI interface"

    def __init__(self, device, interface):
        self.ctx = ftdi.new()
        ftdi.set_interface(self.ctx, interface)
        ftdi.usb_open_dev(self.ctx, device)
        if ftdi.usb_purge_buffers(self.ctx) < 0:
            raise MoxTesterCommunicationException(
                "Buffers purge failed for port: " + str(interface))

    def __del__(self):
        "Close connection to FTDI interface"
        ftdi.deinit(self.ctx)


class _BitBangInterface(_Interface):
    "FTDI interface in Bit Bang mode"

    def __init__(self, device, interface, output_mask, default_value=0x00):
        super().__init__(device, interface)
        if ftdi.set_bitmode(self.ctx, output_mask, ftdi.BITMODE_BITBANG) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set bitbang mode for port: " + str(interface))
        self.value = default_value
        self.gpio_set(output_mask, self.value)

    def gpio(self, mask=0xFF):
        """Read status of pins. It returns read byte. You can use mask to
        automatically mask some bits. In default all bits are read and
        returned."""
        ret, value = ftdi.read_pins(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("Reading pins status failed")
        return int.from_bytes(value, 'big') & mask

    def gpio_set(self, data, mask=0xFF):
        "Write pins status. Whole byte at once."
        self.value = (self.value & (mask ^ 0xFF)) | (data & mask)
        if ftdi.write_data(self.ctx, bytes([self.value])) < 0:
            raise MoxTesterCommunicationException("Write failed")

    def is_set(self, mask=0xFF):
        """Returns True if at least one of bits is set to 1. Mask can be used
        to limit considered bits."""
        return bool(self.gpio(mask))

    def set(self, is_set, mask=0xFF):
        """Sets given bits dependning on is_set boolean value. Bits can be
        selected by mask."""
        self.gpio_set(mask if is_set else 0x00, mask)


class _MPSSEInterface(_Interface):
    "FTDI interface in MPSSE mode"

    def __init__(self, device, interface, output_mask, default_value=0x00):
        super().__init__(device, interface)
        self.output_mask = output_mask & 0xF0  # Mask for GPIO
        if ftdi.set_bitmode(self.ctx, 0x00, ftdi.BITMODE_MPSSE) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set MPSSE mode for port: " + str(interface))
        self.gpio_value = default_value
        self.gpio_set(self.output_mask, self.gpio_value)

    def _write(self, operation):
        "Write given program to MPSSE"
        if ftdi.write_data(self.ctx, operation) < 0:
            raise MoxTesterCommunicationException("MPSSE write failed")

    def _read(self):
        "Read input buffer as bytes"
        ret, chunk_size = ftdi.read_data_get_chunksize(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("Get chunk size failed")
        data = bytes()
        while True:
            ret, new_data = ftdi.read_data(self.ctx, chunk_size)
            if ret < 0:
                raise MoxTesterCommunicationException("MPSSE read failed")
            elif ret > 0:
                data = data + new_data[0:ret]
            else:
                # No more data to be read so return what we have
                return data

    def gpio(self, mask=0xF0):
        """Read current GPIO state. You can limit pins by using mask.
        Note that only four most significant bits are returned unmasked."""
        ret, value = ftdi.read_pins(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("Reading pins status failed")
        return int.from_bytes(value, 'big') & mask

    def gpio_set(self, value, mask=0xF0):
        """Write GPIO state. You can limit pins by using mask. Note that only
        four most significant bits are used."""
        self.gpio_value = (self.gpio_value & (mask ^ 0xFF)) | (value & mask)
        self._write(bytes(
            (ftdi.SET_BITS_LOW, self.gpio_value, self.output_mask)))

    def update_output_mask(self, mask=0xF0):
        """Update mask that is used to set output pins.
        """
        self.output_mask = mask
        self.gpio_set(0x00, 0x00)  # Does no GPIO change except of orientation

    def is_set(self, mask=0xF0):
        """Returns True if at least one of bits is set to 1. Mask can be used
        to limit considered bits."""
        return bool(self.gpio(mask))

    def set(self, is_set, mask=0xF0):
        """Sets given bits dependning on is_set boolean value. Bits can be
        selected by mask."""
        self.gpio_set(mask if is_set else 0x00, mask)


class _SPIInterface(_MPSSEInterface):
    "FTDI interface in MPSSE mode with SPI functionality"

    def __init__(self, device, interface, gpio_output_mask, gpio_default=0x00):
        super().__init__(device, interface, gpio_output_mask, gpio_default)
        if ftdi.setflowctrl(self.ctx, ftdi.SIO_DISABLE_FLOW_CTRL) < 0:
            raise MoxTesterCommunicationException(
                "Flow control setup failed for interface: " + str(interface))
        self.enabled = False
        self._write(bytes((
            ftdi.EN_DIV_5,  # Enable divide by 5 of internal clock
            ftdi.DIS_3_PHASE,  # Disable 3 phase data clocking
            ftdi.DIS_ADAPTIVE,  # Disable adaprive clocking
            ftdi.TCK_DIVISOR, 0, 0,  # Set clock to 6MHz
        )))
        self._burst = None
        self.spi_burst_new()

    def spi_enable(self, enable):
        """Enables/Disables SPI outputs.
        """
        if enable:
            self.gpio_value = (self.gpio_value & 0xF0) | 0x09
            self.update_output_mask((self.output_mask & 0xF0) | 0x0B)
        else:
            self.gpio_value = self.gpio_value & 0xF0
            self.update_output_mask(self.output_mask & 0xF0)
        self.enabled = enable

    def spi_burst_new(self):
        """Drop currently lined up burst."""
        self._burst = bytes()
        self._spi_cs(True)

    def _spi_cs(self, select):
        self._burst = self._burst + bytes((
            ftdi.SET_BITS_LOW,
            (self.gpio_value & 0xF0) | (0x01 if select else 0x09),
            self.output_mask,
        ))

    def spi_burst_cs_reset(self):
        """Add chip select reset to current burst.
        This unsets and sets chip select pin. This is usable when device
        requires you to unselect it to finish single command.
        """
        self._spi_cs(False)
        self._spi_cs(True)

    def spi_burst_read(self, size=1):
        """Add byte read to burst. Number of bytes can be specified in size
        argument."""
        if size < 1 or size > (0x10000):
            raise MoxTesterSPIException(
                "Not supported size for single read: " + str(size))
        self._burst = self._burst + bytes((
            ftdi.MPSSE_DO_READ,
            (size - 1) % 0x100,
            (size - 1) // 0x100,
        ))

    def _spi_burst_write_common(self, size):
        if size < 1 or size > (0x10000):
            raise MoxTesterSPIException(
                "Not supported size for single write: " + str(size))
        self._burst = self._burst + bytes((
            ftdi.MPSSE_DO_WRITE | ftdi.MPSSE_WRITE_NEG,
            (size - 1) % 0x100,
            (size - 1) // 0x100,
        ))

    def spi_burst_write(self, data):
        """Write bytes.
        """
        self._spi_burst_write_common(len(data))
        self._burst = self._burst + data

    def spi_burst_write_int(self, value, size=1, bigendian=True):
        """Write integer as a type of given size in bytes.
        """
        self._spi_burst_write_common(size)
        self._burst = self._burst + value.to_bytes(
            size, 'big' if bigendian else 'little')

    def spi_burst(self):
        """Run prepared burst and return read result.
        Use spi_burst_* methods to add operations to single burst.
        """
        self._spi_cs(False)
        self._write(self._burst)
        data = self._read()
        self.spi_burst_new()
        return data

    def spi_burst_int(self):
        """Run prepared burst and return read result as a single integer
        number. Use spi_burst_* methods to add operations to single burst.
        """
        value = self.spi_burst()
        if value is not None:
            return int.from_bytes(value, 'big')
        return value

    def spi_loopback(self, enable):
        "Set SPI loopback. Note that this automaticaly disabled SPI output."
        self._write(bytes((
            ftdi.LOOPBACK_START if enable else ftdi.LOOPBACK_END,)))
        self.spi_enable(False)
        self.enabled = enable

    def spi_selftest(self):
        """Runs self-test of SPI interface (checks loopback)
        It sends bogus opcode. Respond should be "bad command" (0xFA) and
        invalid opcode. All this is done in loopback mode to not distort
        potential hardware.
        """
        self.spi_loopback(True)
        ftdi.usb_purge_buffers(self.ctx)
        self._write(bytes((0xAB,)))
        read = int.from_bytes(self._read(), 'big')
        if read != 0xFAAB:
            raise MoxTesterSPITestFail("Invalid respond on bogus command " + "(expected 0xfaab but received {})".format(hex(read)))
        self._write(bytes((
            ftdi.MPSSE_DO_READ | ftdi.MPSSE_DO_WRITE | ftdi.MPSSE_READ_NEG,
            0, 0, 0x42,
        )))
        data = int.from_bytes(self._read(), 'big')
        if data != 0x42:
            raise MoxTesterSPITestFail("Invalid value read on loopkback " + "(expected 0x42 but received {})".format(hex(data)))
        self.spi_loopback(False)


class _UARTInterface(_Interface):
    "FTDI interface in Bit Bang mode"

    def __init__(self, device, interface, board_id="unknown", log=True):
        super().__init__(device, interface)
        self.board_id = board_id
        self.log = log
        if ftdi.set_bitmode(self.ctx, 0x00, ftdi.BITMODE_RESET) < 0:
            raise MoxTesterCommunicationException(
                "Unable to reset bitmode for port: " + str(interface))
        if ftdi.set_baudrate(self.ctx, 115200) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set baudrate for port:" + str(interface))
        if ftdi.set_line_property(
                self.ctx, ftdi.BITS_8, ftdi.STOP_BIT_1, ftdi.NONE):
            raise MoxTesterCommunicationException(
                "Line property setup failed for interface: " + str(interface))

        # Input
        self.inputthreadexit = Event()
        # TODO add sensible name
        self.inputthread = Thread(
            target=self._input, daemon=True)
        self.inputthread.start()  # Start input immediately
        # Output
        self.socks = socket.socketpair()
        self.outputthreadexit = Event()
        # TODO add sensible name
        self.outputthread = Thread(target=self._output, daemon=True)
        self.outputthread.start()

    def __del__(self):
        self.inputthreadexit.set()
        self.outputthreadexit.set()
        self.socks[1].close()
        toclose = self.socks[0]
        self.socks = None
        toclose.close()
        self.inputthread.join()
        self.outputthread.join()
        super().__del__()

    def set_board_id(self, board_id="unknown"):
        self.board_id = board_id

    def _chunk_size(self):
        ret, chunk_size = ftdi.read_data_get_chunksize(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("UART get chunk size failed")
        return chunk_size

    def _input(self):
        chunk_size = self._chunk_size()
        prev_data = b''
        while not self.inputthreadexit.is_set():
            ret, data = ftdi.read_data(self.ctx, chunk_size)
            if ret < 0:
                raise MoxTesterCommunicationException("UART Read failed")
            elif ret > 0:
                import logging
                logging.error(data[0:ret])
                self.socks[0].sendall(data[0:ret])
                new_data = data[0:ret]
                index = new_data.find(b'\n')
                if index >= 0:
                    report.log('UART({}): '.format(self.board_id) + str(prev_data + new_data[0:index + 1]))
                    prev_data = new_data[index:]
                else:
                    prev_data = prev_data + new_data
            else:
                # Sleep for short amount of time to not busyloop
                sleep(0.01)

    def _output(self):
        chunk_size = self._chunk_size()
        while not self.outputthreadexit.is_set():
            data = self.socks[0].recv(chunk_size)
            # TODO do we want to log this also?
            if ftdi.write_data(self.ctx, data) < 0:
                raise MoxTesterCommunicationException("UART Write failed")

    def fileno(self):
        "Create new file descriptior (while closing the old one) and return it"
        return self.socks[1].fileno()

    def pexpect(self):
        "Returns fdpexpect handle."
        return fdpexpect.fdspawn(self.socks[1])
