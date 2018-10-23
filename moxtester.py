import io
import socket
from time import sleep
from threading import Thread, Event
from pexpect import fdpexpect
import ftdi1 as ftdi
from moxtester_spiflash import SPIFlash


class MoxTester:
    "Class controlling one specific mox tester."
    BOOT_MODE_SPI = 0b01
    BOOT_MODE_UART = 0b10

    def __init__(self, chip_id):
        ctx = ftdi.new()
        ret, devs = ftdi.usb_find_all(ctx, 0x0403, 0x6011)
        if ret < 0:
            raise MoxTesterCommunicationException("Unable to list USB devices")
        dev = None
        while dev is None and devs is not None:
            # Ignore any device that fails open (those are in use)
            if ftdi.usb_open_dev(ctx, devs.dev) == 0:
                if ftdi.read_eeprom(ctx) < 0:
                    raise MoxTesterCommunicationException("EEPROM read failed")
                if ftdi.eeprom_decode(ctx, 0) < 0:
                    raise MoxTesterCommunicationException(
                        'EEPROM decode failed')
                ret, chip_tp = ftdi.get_eeprom_value(ctx, ftdi.CHIP_TYPE)
                if ret < 0:
                    raise MoxTesterCommunicationException(
                        "Reading chip type (id) failed")
                if chip_tp == chip_id:
                    dev = devs.dev  # Setting dev if correct device found
                ftdi.usb_reset(ctx)
                ftdi.usb_close(ctx)
            devs = devs.next
        if dev is None:
            raise MoxTesterNotFoundException(
                "There is no connected tester with id: " + str(chip_id))

        # CN1 (detection, power supply and JTAG)
        self._a = _BitBangInterface(dev, ftdi.INTERFACE_A, 0x40)
        self.power(False)
        # CN2 (boot mode, hardware reset and SPI)
        self._b = _SPIInterface(dev, ftdi.INTERFACE_B, 0xE0)
        self.reset(True)
        self.set_boot_mode(self.BOOT_MODE_SPI)
        # CN3 (Unused GPIO)
        self._c = _BitBangInterface(dev, ftdi.INTERFACE_C, 0x00)
        # CN4 (UART)
        self._d = _UARTInterface(dev, ftdi.INTERFACE_D)
        self._uart = None

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
            self._b.gpio_set(0xC0, 0xC0)
        elif mode == self.BOOT_MODE_UART:
            self._b.gpio_set(0x00, 0xC0)
        else:
            raise MoxTesterInvalidMode(
                "Trying to set invalid mode: {}".format(mode))

    def reset(self, enabled):
        "Set hardware reset pin of board."
        self._b.set(enabled, 0x20)

    def uart(self):
        "Returns fdpexpect object for comunication with UART"
        return self._d.pexpect()

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


def _common_interface_ctx(device, interface):
    ctx = ftdi.new()
    ftdi.set_interface(ctx, interface)
    ftdi.usb_open_dev(ctx, device)
    if ftdi.usb_purge_buffers(ctx) < 0:
        raise MoxTesterCommunicationException(
            "Buffers purge failed for port: " + str(interface))
    return ctx


class _BitBangInterface():
    "FTDI interface in Bit Bang mode"

    def __init__(self, device, interface, output_mask, default_value=0x00):
        self.ctx = _common_interface_ctx(device, interface)
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


class _MPSSEInterface():
    "FTDI interface in MPSSE mode"

    def __init__(self, device, interface, output_mask, default_value=0x00):
        self.output_mask = output_mask & 0xF0  # Mask for GPIO
        self.ctx = _common_interface_ctx(device, interface)
        if ftdi.set_bitmode(self.ctx, 0x00, ftdi.BITMODE_MPSSE) < 0:
            raise MoxTesterCommunicationException(
                "Unable to set MPSSE mode for port: " + str(interface))
        self.gpio_value = default_value
        self.gpio_set(output_mask, self.gpio_value)

    def _write(self, operation):
        "Write given program to MPSSE"
        if not isinstance(operation, tuple) and not isinstance(operation, list):
            raise MoxTesterException(
                "MPSSE Invalid write type:" + str(type(operation)))
        if ftdi.write_data(self.ctx, bytes(operation)) < 0:
            raise MoxTesterCommunicationException("MPSSE write failed")

    def _read(self):
        "Read input buffer as bytes"
        ret, chunk_size = ftdi.read_data_get_chunksize(self.ctx)
        if ret < 0:
            raise MoxTesterCommunicationException("Get chunk size failed")
        ret, data = ftdi.read_data(self.ctx, chunk_size)
        if ret < 0:
            raise MoxTesterCommunicationException("MPSSE read failed")
        elif ret > 0:
            return data[0:ret]
        else:
            return None

    def _read_int(self):
        "Read input buffer as a single number"
        value = self._read()
        if value is not None:
            return int.from_bytes(value, 'big')
        return value

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
        self._write((ftdi.SET_BITS_LOW, self.gpio_value, self.output_mask))

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
        self._write((
            ftdi.EN_DIV_5,  # Enable divide by 5 of internal clock
            ftdi.DIS_3_PHASE,  # Disable 3 phase data clocking
            ftdi.DIS_ADAPTIVE,  # Disable adaprive clocking
            ftdi.TCK_DIVISOR, 0, 0,  # Set clock to 6MHz
            ))
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
        self._burst = []
        self._spi_cs(True)

    def _spi_cs(self, select):
        self._burst.append(ftdi.SET_BITS_LOW)
        self._burst.append(
            (self.gpio_value & 0xF0) | (0x01 if select else 0x09))
        self._burst.append(self.output_mask)

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
        self._burst.append(ftdi.MPSSE_DO_READ)
        self._burst.append((size - 1) % 0xFF)
        self._burst.append((size - 1) // 0xFF)

    def spi_burst_write_int(self, value, size=1):
        """Write integer as a type of given size in bytes.
        """
        self._burst.append(ftdi.MPSSE_DO_WRITE | ftdi.MPSSE_WRITE_NEG)
        self._burst.append((size - 1) % 0xFF)
        self._burst.append((size - 1) // 0xFF)
        for i in range(size):
            self._burst.append((value >> 8*i) & 0xFF)

    def spi_burst_swap_int(self, value, size=1):
        """Swap given amount of bytes with target device. This means that write
        and read is executed together. First value is written and then it is
        read."""
        self._burst.append(
            ftdi.MPSSE_DO_READ | ftdi.MPSSE_DO_WRITE | ftdi.MPSSE_READ_NEG)
        self._burst.append((size - 1) % 0xFF)
        self._burst.append((size - 1) // 0xFF)
        for i in range(size):
            self._burst.append((value >> 8*i) & 0xFF)

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
        self._write((
            ftdi.LOOPBACK_START if enable else ftdi.LOOPBACK_END,))
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
        self._write((0xAB,))
        read = self._read_int()
        if read != 0xFAAB:
            raise MoxTesterSPITestFail(
                "Invalid respond on bogus command " +
                "(expected 0xfaab but received {})".format(hex(read)))
        self.spi_burst_new()
        self.spi_burst_swap_int(0x42, 1)
        data = self.spi_burst_int()
        if data != 0x42:
            raise MoxTesterSPITestFail(
                "Invalid value read on loopkback " +
                "(expected 0x42 but received {})".format(hex(data)))
        self.spi_loopback(False)


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
        if ftdi.set_line_property(
                self.ctx, ftdi.BITS_8, ftdi.STOP_BIT_1, ftdi.NONE):
            raise MoxTesterCommunicationException(
                "Line property setup failed for interface: " + str(interface))

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


class MoxTesterNotFoundException(MoxTesterException):
    """Mox tester of provided id is not connected to this PC or is in use
    already."""
    pass


class MoxTesterCommunicationException(MoxTesterException):
    """Exception raised by MoxTester when problem is encountered durring tester
    communication."""
    pass


class MoxTesterInvalidMode(MoxTesterException):
    """Trying to set invalid mode."""
    pass


class MoxTesterSPIException(MoxTesterException):
    """SPI generic exceptionn."""
    pass


class MoxTesterSPITestFail(MoxTesterSPIException):
    """SPI test of Mox tester failed for some reason."""
    pass
