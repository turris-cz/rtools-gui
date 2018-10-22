

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

    def reset(self):
        """Reset SPI flash.
        After calling this you should give device at least 30us to reset it
        self."""
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._RESET_DEVICE)
        self.spi.spi_burst()

    def reset_enable(self):
        """Enable SPI flash reset.
        You have to call this before reset()"""
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._ENABLE_RESET)
        self.spi.spi_burst()

    def write_enable(self, enable):
        "Set if write is enabled"
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(
            self._WRITE_ENABLE if enable else self._WRITE_DISABLE)
        self.spi.spi_burst()

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
        return self.spi.spi_burst()

    def jedec_id(self):
        "Returns JEDEC ID"
        self.spi.spi_burst_new()
        self.spi.spi_burst_write_int(self._JEDEC_ID)
        self.spi.spi_burst_read(3)
        return self.spi.spi_burst()
