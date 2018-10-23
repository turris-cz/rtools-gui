
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


class MoxTesterSPIFLashUnalignedException(MoxTesterSPIException):
    """Address used in SPIFlash is not correctly aligned."""
    pass
