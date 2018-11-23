import os
import sys
import stat
import hashlib
import socket
import subprocess
from shutil import copyfile
import pexpect

DIR_PREFIX = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SECURE_FIRMWARE = os.path.join(DIR_PREFIX, "firmware/untrusted-secure-firmware")
TRUSTED_SECURE_FIRMWARE = os.path.join(DIR_PREFIX, "firmware/secure-firmware")
# TODO use only one single secure firmware (trusted one) -> drop untrusted one
UBOOT = os.path.join(DIR_PREFIX, "firmware/u-boot")
RESCUE = os.path.join(DIR_PREFIX, "firmware/image.fit.lzma")
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
        self.__uboot, self.__uboot_hash = _load_file(UBOOT)
        self.__rescue, self.__rescue_hash = _load_file(RESCUE)
        self.__dtb, self.__dtb_hash = _load_file(DTB)
        self.__hostname = socket.gethostname()
        self.__rtools_git = _git_head_hash(DIR_PREFIX)
        self.__mox_imager_git = _git_head_hash(MOX_IMAGER_DIR)

        # Mox imager
        # TODO exception when there is no executable
        with open(MOX_IMAGER, 'rb') as file:
            self.__mox_imager_hash = hashlib.sha256(file.read()).hexdigest()
        self.__mox_imager_exec = os.path.join(
            conf.tmp_dir, 'rtools-mox-imager-' + self.__mox_imager_hash)
        copyfile(MOX_IMAGER, self.__mox_imager_exec)
        os.chmod(self.__mox_imager_exec,
                 os.stat(self.__mox_imager_exec).st_mode | stat.S_IEXEC)
        # Hash for moximager
        with pexpect.spawn(self.mox_imager_exec, ['--get-otp-hash', TRUSTED_SECURE_FIRMWARE]) as pexp:
            pexp.expect(['Secure firmware OTP hash: '])
            pexp.expect([r'\S{64}'])
            self.__mox_imager_secure_firmware_hash = pexp.after.decode(sys.getdefaultencoding())

    @property
    def secure_firmware(self):
        "Bytes of secure firmware"
        return self.__secure_firmware

    @property
    def secure_firmware_hash(self):
        "Sha256 hash of secure firmware"
        return self.__secure_firmware_hash

    @property
    def uboot(self):
        "Bytes of u-boot image"
        return self.__uboot

    @property
    def uboot_hash(self):
        "Sha256 hash of u-boot image"
        return self.__uboot_hash

    @property
    def rescue(self):
        "Bytes of rescue image"
        return self.__rescue

    @property
    def rescue_hash(self):
        "Sha256 hash of rescue image"
        return self.__rescue_hash

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
