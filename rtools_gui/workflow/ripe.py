"Module implementing steps for Ripe Atlas (A like module)"
import ipaddress
import pathlib
import time
import typing
import zlib
import logging

from pexpect.exceptions import EOF

logger = logging.getLogger(__name__)

from tempfile import NamedTemporaryFile
from .generic import Step, OTPProgramming
from .exceptions import RandomErrorException

MEM_START = "0x01000000"
EXTRACTED = "0x02000000"

class TFTPServerMixin:
    @property
    def tftp_server_ip(self):
        return ipaddress.ip_address(self.conf.tftp_ip)

    @property
    def tftp_client_ip(self):
        return self.tftp_server_ip + (1 + self.moxtester.tester_id)

    @property
    def tftp_dir(self):
        return pathlib.Path(self.conf.tftp_dir)

    @property
    def tftp_image_crc32_and_size(self) -> typing.Tuple[bytes, int]:
        return zlib.crc32(self.resources.flashing_image), len(self.resources.flashing_image)

    def make_tftp_image(self):
        from ..tftp import TFTPFile
        return TFTPFile(self.conf.tftp_dir, self.resources.flashing_image)


class UBootMixin:

    def ubootcmd(self, cmd, expect=None, timeout=-1, sleep=None) -> int:
        self.uart.sendline(cmd)
        if isinstance(expect, list):
            exp = expect
        else:
            exp = [expect or '=>']
        idx = self.uart.expect(exp, timeout=timeout)
        if idx is None:
            raise EOF

        if sleep:
            time.sleep(sleep)

        return idx

class UARTBoot(Step):
    "Load and run firmware (U-boot) by UART"

    def run(self):
        firmware = NamedTemporaryFile()
        try:
            self.set_progress(0)
            firmware.write(self.resources.untrusted_secure_firmware_ripe)
            firmware.write(self.resources.uboot_ripe)
            self.set_progress(0.05)

            imager = self.moxtester.mox_imager(self.resources)
            imgpe = imager.run(firmware.name, '-b', '3000000')
            imager.match("Sending image type TIMH")
            self.set_progress(0.1)
            imager.match("Sending image type WTMI")
            self.set_progress(0.2)
            imager.match("Sending image type OBMI")
            imgpe.expect_exact('.\n', timeout=None)
            imager.stop()

            self.set_progress(1)
        finally:
            firmware.close()

        uart = self.moxtester.uart()
        uart.expect(['Hit any key to stop autoboot'])
        uart.sendline('')
        uart.expect(['=>'])

    @staticmethod
    def name():
        return "Nahrání dočasného systému"

    @staticmethod
    def id():
        return "uboot"

class DownloadFlasher(UBootMixin, TFTPServerMixin, Step):
    "Download flasher to memory"


    def run(self):
        self.set_progress(0)
        self.uart = self.moxtester.uart()

        self.ubootcmd('setenv ethaddr {}'.format(self.db_board.mac_wan()), sleep=1.0)
        self.ubootcmd('setenv autoload no', sleep=1.0)
        self.ubootcmd('setenv bootargs "earlyprintk srv={} console=ttyMV0,115200 earlycon=ar3700_uart,0xd0012000"'.format(self.tftp_server_ip), sleep=1.0)
        self.set_progress(0.03)
        self.ubootcmd('dhcp', 'DHCP client bound', sleep=1.0)
        self.set_progress(0.06)
        self.ubootcmd('setenv serverip {}'.format(self.tftp_server_ip), sleep=1.0)
        self.set_progress(0.1)

        image = self.make_tftp_image()
        image_filename = pathlib.Path(image.name).name

        # make sure that connection is working properly
        idx = self.ubootcmd(
            'ping {}'.format(self.tftp_server_ip),
            ['host {}'.format(self.tftp_server_ip), 'bad rx status'],
            sleep=1.0,
        )

        if(idx != 0):
            raise RandomErrorException("Nahodna sitova chyba, prosim spustte flashovani znova")

        self.set_progress(0.1)

        # Load image from tftp to memory
        idx = self.ubootcmd(
            'tftpboot {} {}'.format(MEM_START, image_filename),
            [ 'Bytes transferred', 'bad rx status'],
            timeout=30,
            sleep=1.0,
         )

        if(idx != 0):
            raise RandomErrorException("Nahodna sitova chyba, prosim spustte flashovani znova")

        self.ubootcmd('')
        self.set_progress(0.1)

        # check crc
        crc32, size = self.tftp_image_crc32_and_size
        self.ubootcmd(
                'crc32 {} {:X}'.format(MEM_START, size),
                '{:x}'.format(crc32),
            timeout=10,
            sleep=1.0,
         )

        self.ubootcmd('')
        self.set_progress(1)

    @staticmethod
    def name():
        return "Stažení flashovacího systému do zařízení"

    @staticmethod
    def id():
        return "download"


class FlashSystem(UBootMixin, Step):
    "Flash OS system to NAND"

    def run(self):
        self.set_progress(0)
        self.uart = self.moxtester.uart()

        # Extract Image
        self.ubootcmd(
            'lzmadec {} {}'.format(MEM_START, EXTRACTED),
            'Uncompressed size:',
            sleep=1.0,
        )
        self.set_progress(0.1)

        # Boot image
        self.ubootcmd(
            'bootm {}'.format(EXTRACTED),
            'Starting kernel ...',
            sleep=1,
            timeout=20,  # TODO limit it based on that how long it actually takes
        )
        self.set_progress(0.2)

        self.uart.expect('Downloading NOR content')
        self.set_progress(0.3)
        self.uart.expect('Downloading rootfs content')
        self.set_progress(0.4)
        self.uart.expect('Deploying .* image', timeout=240)
        self.set_progress(0.6)
        idx = self.uart.expect(['Create a snapshot of', 'mmc1: error -110 whilst initialising MMC card'], timeout=60)
        if(idx != 0):
            raise RandomErrorException("Nahodna MMC chyba, prosim spustte flashovani znova")
        self.set_progress(0.8)
        self.uart.expect('Updating NOR', timeout=600)
        self.set_progress(0.85)
        self.uart.expect('Success - everything reflashed')
        self.set_progress(1)

    @staticmethod
    def name():
        return "Zapsání systému na úložiště"

    @staticmethod
    def id():
        return "flash"

class OTPProgrammingRIPE(OTPProgramming):
    def otp_board_type(self):
        return "RIPE"

    def otp_hash(self):
        return self.resources.mox_imager_secure_firmware_ripe_hash

# All steps for MOX RIPE in order
RSTEPS = (
    UARTBoot,
    DownloadFlasher,
    FlashSystem,
    OTPProgrammingRIPE,
)
