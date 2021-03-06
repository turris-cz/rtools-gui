from time import sleep
from .exceptions import MoxTesterSPIFLashUnalignedException


class SPIFlash():
    "Flash storage manipulator."
    _WRITE_DISABLE = 0x04
    _WRITE_ENABLE = 0x06
    _READ_STATUS_REGISTER_1 = 0x05
    _READ_STATUS_REGISTER_2 = 0x35
    _READ_STATUS_REGISTER_3 = 0x15
    _JEDEC_ID = 0x9F
    _ENABLE_RESET = 0x66
    _RESET_DEVICE = 0x99
    _CHIP_ERASE = 0x60  # 0xC7 seems to be also valid
    _SECTOR_ERASE = 0x20
    _PAGE_PROGRAM = 0x02
    _READ_DATA = 0x03

    def __init__(self, moxtester, spi_interface):
        self.moxtester = moxtester
        self.spi = spi_interface

    def __enter__(self):
        self.spi.spi_enable(True)
        # Note: setting boot mode to UART is required because otherwise CPU has
        # SPI ports configured as outputs and interferes with our SPI usage.
        # This is happening even if CPU is in reset!
        self.moxtester.set_boot_mode(self.moxtester.BOOT_MODE_UART)
        self.moxtester.reset(True)
        self.moxtester.power(True)
        return self

    def __exit__(self, etype, value, traceback):
        self.moxtester.power(False)
        self.moxtester.set_boot_mode(self.moxtester.BOOT_MODE_SPI)
        # Note: left CPU in reset
        self.spi.spi_enable(False)

    def reset_device(self):
        """Reset SPI Flash device and suspends execution for time to ensure
        device reset completion."""
        self.busy_wait()
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._ENABLE_RESET)
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._RESET_DEVICE)
        self.spi.spi_burst()
        sleep(0.001)  # This should be longer than 30us
        # Note: Documentation states that reset takes approximately 30us.
        # Originally 100us was used but it sometimes wasn't enough. Because of
        # that it was increased to 1ms. If there is any other case when for
        # some reason flashing fails then it might be again because of this and
        # this time can be even increased.

    def write_enable(self, enable):
        "Set if write is enabled"
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(
            self._WRITE_ENABLE if enable else self._WRITE_DISABLE)
        self.spi.spi_burst_int()

    def status_registers(self):
        "Return status register"
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._READ_STATUS_REGISTER_3)
        self.spi.spi_burst_read()
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._READ_STATUS_REGISTER_2)
        self.spi.spi_burst_read()
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._READ_STATUS_REGISTER_1)
        self.spi.spi_burst_read()
        return self.spi.spi_burst_int()

    def jedec_id(self):
        "Returns JEDEC ID"
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._JEDEC_ID)
        self.spi.spi_burst_read(3)
        return self.spi.spi_burst_int()

    def is_busy(self):
        "Returns True or False depending on if SPI Flash is busy or not."
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._READ_STATUS_REGISTER_1)
        self.spi.spi_burst_read()
        return bool(self.spi.spi_burst_int() & 0x01)

    def busy_wait(self):
        "Busy wait until SPI Flash is not busy."
        while self.is_busy():
            pass

    def read_data(self, address, size=1, callback=None):
        """Read data from SPI flash from given address. At single read it is
        possible to read multiple bytes. Fot that purpose you can use size
        argument.
        callback(progress) argument is optional function that is called with
        progress update. Progress is float value between 0 and 1."""
        # We have maximum amount of possible read bytes per single read so we
        # have to do it multiple times
        sectors = self._sectors_count(size, 0x10000)
        data = bytes()
        for i in range(sectors):
            self.spi.spi_burst_new()
            self.spi.spi_burst_write_int(self._READ_DATA)
            self.spi.spi_burst_write_int(address + (0x10000 * i), 3)
            if i >= (sectors - 1) and size % 0x10000 != 0:
                self.spi.spi_burst_read(size % 0x10000)
            else:
                self.spi.spi_burst_read(0x10000)
            data = data + self.spi.spi_burst()
            if callback is not None:
                callback((i + 1) / sectors)
        return data

    def chip_erase(self):
        """Erase content of chip."""
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._WRITE_ENABLE)
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._CHIP_ERASE)
        self.spi.spi_burst()
        self.busy_wait()

    def sector_erase(self, address):
        """Erase single 4KB sector."""
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._WRITE_ENABLE)
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._SECTOR_ERASE)
        self.spi.spi_burst_write_int(address, 3)
        self.spi.spi_burst()
        self.busy_wait()

    def write_page(self, address, data):
        """Write data to single page (256B) in SPI Flash.
        Page has to be erased before write is attempted.
        """
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._WRITE_ENABLE)
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._PAGE_PROGRAM)
        self.spi.spi_burst_write_int(address, 3)
        self.spi.spi_burst_write(data)
        self.spi.spi_burst()
        # Note: this is at maximum shorther than it takes us to check for busy
        # state (around 40ms). Because of that we use sleep here instead.
        sleep(0.005)

    @staticmethod
    def _sectors_count(data_len, sector_size):
        """Returns number of sectors for given data to fit to if sector has
        sector_size.
        data_len: number of bytes of data
        sector_size: number of bytes per sector"""
        res = data_len // sector_size
        if (data_len % sector_size) > 0:
            res = res + 1
        return res

    def write_data(self, address, data, callback=None):
        """Write given data from given address of memory. You should wipe
        target sector before calling this function. After wipe you can call
        this multiple times but only on non-overlapping sections."""
        sectors = self._sectors_count(len(data), 0x100)
        for i in range(sectors):
            self.write_page(address + (256 * i), data[(256 * i):(256 * (i + 1))])
            if callback is not None:
                callback((i + 1) / sectors)

    def write(self, address, data, callback=None):
        """Write data to given address. This method tries to be smart and does
        as little as possible. It wipes memory at 4KB sectors and does that
        only if data in memory does not match provided data."""
        if address & 0xFFF != 0:  # Just to make this code simple
            raise MoxTesterSPIFLashUnalignedException(
                "Write has to be aligned to 4KB sector")
        if callback is not None:
            callback(0)
        size = len(data)
        # First read current state
        current = self.read_data(
            address, size, None if callback is None else
            lambda p: callback(p * .2))
        # Go trough 4K sectors (minimum size to erase)
        secnum = self._sectors_count(size, 0x1000)
        for i in range(secnum):
            if callback is not None:
                callback(.2 + .8 * (i / secnum))
            secaddr = address + (i * 0x1000)
            target = data[(i * 0x1000):((i + 1) * 0x1000)]
            currsec = current[(i * 0x1000):((i + 1) * 0x1000)]
            wipe = False
            for y in range(len(target)):
                wipe = wipe or ((currsec[y] ^ 0xff) & target[y])
            if wipe:
                self.sector_erase(secaddr)  # Erase only if it is required
            for y in range(self._sectors_count(len(target), 0x100)):
                page = target[(256 * y):(256 * (y + 1))]
                if wipe or page != currsec[(256 * y):(256 * (y + 1))]:
                    self.write_page(secaddr + (256 * y), page)
        if callback is not None:
            callback(1)

    def verify(self, address, data, callback=None):
        """Verify content of SPI Flash that from given address it contains
        given data."""
        current = self.read_data(
            address, len(data), None if callback is None else
            lambda progress: callback(progress * .95))
        assert len(current) == len(data)
        result = data == current
        if callback is not None:
            callback(1)
        return result
