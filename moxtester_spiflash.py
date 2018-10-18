

class SPIFlash():
    "Flash storage manipulator."
    _WRITE_DISABLE = 0x04
    _WRITE_ENABLE = 0x06
    _READ_STATUS_REGISTER_1 = 0x05
    _READ_STATUS_REGISTER_2 = 0x35
    _READ_STATUS_REGISTER_3 = 0x15
    _JEDEC_ID = 0x9F

    def __init__(self, moxtester, spi_interface):
        self.moxtester = moxtester
        self.spi = spi_interface

    def __enter__(self):
        self.spi.spi_enable(True)
        self.moxtester.reset(True)
        self.moxtester.power(True)
        return self

    def __exit__(self ,type, value, traceback):
        self.moxtester.power(False)
        self.moxtester.reset(False)
        self.spi.spi_enable(False)

    def reset(self):
        self.spi.spi_burst((
            (self.spi.SPI_WRITE, 1, 0x99),
            ))

    def reset_enable(self):
        self.spi.spi_burst((
            (self.spi.SPI_WRITE, 1, 0x66),
            ))

    def write_enable(self, enable):
        "Set if write is enabled"
        self.spi.spi_burst((
            (self.spi.SPI_WRITE, 1,
             self._WRITE_ENABLE if enable else self._WRITE_DISABLE),
            ))

    def status_registers(self):
        "Return status register"
        return self.spi.spi_burst((
            (self.spi.SPI_WRITE, 1, self._READ_STATUS_REGISTER_1),
            (self.spi.SPI_READ, 1),
            (self.spi.SPI_WRITE, 1, self._READ_STATUS_REGISTER_2),
            (self.spi.SPI_READ, 1),
            (self.spi.SPI_WRITE, 1, self._READ_STATUS_REGISTER_3),
            (self.spi.SPI_READ, 1),
            ))

    def jedec_id(self):
        "Returns JEDEC ID"
        return self.spi.spi_burst((
            (self.spi.SPI_WRITE, 1, self._JEDEC_ID),
            (self.spi.SPI_READ, 3),
            ))
