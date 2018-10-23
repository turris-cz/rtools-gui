from time import sleep


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
    _READ_DATA = 0x03

    def __init__(self, moxtester, spi_interface):
        self.moxtester = moxtester
        self.spi = spi_interface

    def __enter__(self):
        self.spi.spi_enable(True)
        self.moxtester.reset(True)
        self.moxtester.power(True)
        return self

    def __exit__(self, etype, value, traceback):
        self.moxtester.power(False)
        self.moxtester.reset(False)
        self.spi.spi_enable(False)

    def reset_device(self):
        """Reset SPI Flash device and suspends execution for time to ensure
        device reset completion."""
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._RESET_DEVICE)
        self.spi.spi_burst_cs_reset()
        self.spi.spi_burst_write_int(self._ENABLE_RESET)
        self.spi.spi_burst()
        sleep(0.0001)  # This should be longer than 30us

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
        self.spi.spi_burst_cs_reset()
        return self.spi.spi_burst_int()

    def jedec_id(self):
        "Returns JEDEC ID"
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._JEDEC_ID)
        self.spi.spi_burst_read(3)
        return self.spi.spi_burst_int()

    def read_data(self, address, size=1):
        """Read data from SPI flash from given address. At single read it is
        possible to read multiple bytes. Fot that purpose you can use size
        argument."""
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._READ_DATA)
        self.spi.spi_burst_write_int(address, 3)
        self.spi.spi_burst_read(size)
        return self.spi.spi_burst()
