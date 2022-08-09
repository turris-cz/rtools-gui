import os
import pathlib
import sys
import stat
import hashlib
import socket
import subprocess
from shutil import copyfile
import pexpect

DIR_PREFIX = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SECURE_FIRMWARE = os.path.join(DIR_PREFIX, "firmware/secure-firmware")
SECURE_FIRMWARE_RIPE = os.path.join(DIR_PREFIX, "firmware/secure-firmware-ripe")
UNTRUSTED_SECURE_FIRMWARE = os.path.join(DIR_PREFIX, "firmware/untrusted-secure-firmware")
UNTRUSTED_SECURE_FIRMWARE_RIPE = os.path.join(DIR_PREFIX, "firmware/untrusted-secure-firmware-ripe")
WHOLE_UNTRUSTED_FIRMWARE_RIPE = os.path.join(DIR_PREFIX, "firmware/whole-untrusted-firmware-ripe")
UBOOT = os.path.join(DIR_PREFIX, "firmware/u-boot")
UBOOT_RIPE = os.path.join(DIR_PREFIX, "firmware/u-boot-ripe")
RESCUE = os.path.join(DIR_PREFIX, "firmware/image.fit.lzma")
FLASHING_IMAGE = os.path.join(DIR_PREFIX, "firmware/ripe-flasher.fit.lzma")
DTB = os.path.join(DIR_PREFIX, "firmware/dtb")
MOX_IMAGER_DIR = os.path.join(DIR_PREFIX, "mox-imager")
MOX_IMAGER = os.path.join(MOX_IMAGER_DIR, "mox-imager")


def _load_file(path):
    with open(path, 'rb') as file:
        data = file.read()
    hsh = hashlib.sha256(data).hexdigest()
    return data, hsh


def _git_head_hash(path):
    curdir = os.getcwd()
    os.chdir(path)
    process = subprocess.run(
        ['git', 'describe', '--long', '--always', '--dirty'],
        stdout=subprocess.PIPE)
    githash = process.stdout.decode(sys.getdefaultencoding()).strip()
    os.chdir(curdir)
    return githash


class Resources:
    "Resources used by rtools-gui"

    def __init__(self, conf):
        self.__secure_firmware, self.__secure_firmware_hash = _load_file(SECURE_FIRMWARE)
        self.__secure_firmware_ripe, self.__secure_firmware_ripe_hash = _load_file(SECURE_FIRMWARE_RIPE)
        self.__untrusted_secure_firmware, self.__untrusted_secure_firmware_hash = _load_file(UNTRUSTED_SECURE_FIRMWARE)
        self.__untrusted_secure_firmware_ripe, self.__untrusted_secure_firmware_ripe_hash = _load_file(UNTRUSTED_SECURE_FIRMWARE_RIPE)
        self.__uboot, self.__uboot_hash = _load_file(UBOOT)
        self.__uboot_ripe, self.__uboot_ripe_hash = _load_file(UBOOT_RIPE)
        self.__rescue, self.__rescue_hash = _load_file(RESCUE)
        self.__flashing_image, self.__flashing_image_hash = _load_file(FLASHING_IMAGE)
        self.__dtb, self.__dtb_hash = _load_file(DTB)
        self.__hostname = socket.gethostname()
        self.__rtools_git = _git_head_hash(DIR_PREFIX)
        self.__mox_imager_git = _git_head_hash(MOX_IMAGER_DIR)

        # Mox imager
        imager_path = pathlib.Path(MOX_IMAGER)
        if not imager_path.exists():
            raise RuntimeError("No mox imager binary found in {}".format(imager_path))
        with imager_path.open('rb') as file:
            self.__mox_imager_hash = hashlib.sha256(file.read()).hexdigest()
        self.__mox_imager_exec = MOX_IMAGER

        # Hashes for moximager
        self.__mox_imager_secure_firmware_hash = self._otp_hash(SECURE_FIRMWARE)
        self.__mox_imager_secure_firmware_ripe_hash = self._otp_hash(SECURE_FIRMWARE_RIPE)

    def _otp_hash(self, path):
        # Hash for moximager
        with pexpect.spawn(self.mox_imager_exec, ['--get-otp-hash', path]) as pexp:
            pexp.expect(['Secure firmware OTP hash: '])
            pexp.expect([r'\S{64}'])
            return pexp.after.decode(sys.getdefaultencoding())

    @property
    def secure_firmware(self):
        "Bytes of secure firmware"
        return self.__secure_firmware

    @property
    def secure_firmware_hash(self):
        "Sha256 hash of secure firmware"
        return self.__secure_firmware_hash

    @property
    def secure_firmware_ripe(self):
        "Bytes of secure firmware ripe"
        return self.__secure_firmware_ripe

    @property
    def secure_firmware_ripe_hash(self):
        "Sha256 hash of secure firmware ripe"
        return self.__secure_firmware_ripe_hash

    @property
    def untrusted_secure_firmware(self):
        "Bytes of secure firmware"
        return self.__untrusted_secure_firmware

    @property
    def untrusted_secure_firmware_hash(self):
        "Sha256 hash of secure firmware"
        return self.__untrusted_secure_firmware_hash

    @property
    def untrusted_secure_firmware_ripe(self):
        "Bytes of secure firmware ripe"
        return self.__untrusted_secure_firmware_ripe

    @property
    def whole_untrusted_firmware_ripe_path(self):
        "Path of the whole firmware for ripe"
        return WHOLE_UNTRUSTED_FIRMWARE_RIPE

    @property
    def untrusted_secure_firmware_ripe_hash(self):
        "Sha256 hash of secure firmware ripe"
        return self.__untrusted_secure_firmware_ripe_hash

    @property
    def uboot(self):
        "Bytes of u-boot image"
        return self.__uboot

    @property
    def uboot_hash(self):
        "Sha256 hash of u-boot image"
        return self.__uboot_hash

    @property
    def uboot_ripe(self):
        "Bytes of u-boot-ripe image"
        return self.__uboot_ripe

    @property
    def uboot_ripe_hash(self):
        "Sha256 hash of u-boot image"
        return self.__uboot_ripe_hash

    @property
    def rescue(self):
        "Bytes of rescue image"
        return self.__rescue

    @property
    def rescue_hash(self):
        "Sha256 hash of rescue image"
        return self.__rescue_hash

    @property
    def flashing_image(self):
        "Bytes of flashing image"
        return self.__flashing_image

    @property
    def flashing_image_hash(self):
        "Sha256 hash of flashing image"
        return self.__flashing_image

    @property
    def dtb(self):
        "Bytes of device tree"
        return self.__dtb

    @property
    def dtb_hash(self):
        "Sha256 hash of device tree"
        return self.__dtb_hash

    @property
    def hostname(self):
        "Hostname of machine programmator is running on"
        return self.__hostname

    @property
    def rtools_git(self):
        "Git hash of rtools-gui repository HEAD"
        return self.__rtools_git

    @property
    def mox_imager_git(self):
        "Git hash of mox-imager submodule HEAD"
        return self.__mox_imager_git

    @property
    def mox_imager_hash(self):
        "mox-imager executable sha256 hash"
        return self.__mox_imager_hash

    @property
    def mox_imager_exec(self):
        "Path to mox-imager executable"
        return self.__mox_imager_exec

    @property
    def mox_imager_secure_firmware_hash(self):
        "Hash from secure-firmware for mox-imager"
        return self.__mox_imager_secure_firmware_hash

    @property
    def mox_imager_secure_firmware_ripe_hash(self):
        "Hash from secure-firmware-ripe for mox-imager"
        return self.__mox_imager_secure_firmware_ripe_hash
