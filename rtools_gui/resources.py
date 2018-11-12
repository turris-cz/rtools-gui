import os
import sys
import hashlib
import socket
import subprocess

DIR_PREFIX = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SECURE_FIRMWARE = os.path.join(DIR_PREFIX, "firmware/secure-firmware")
UBOOT = os.path.join(DIR_PREFIX, "firmware/u-boot")
RESCUE = os.path.join(DIR_PREFIX, "firmware/image.fit.lzma")
DTB = os.path.join(DIR_PREFIX, "firmware/dtb")


def _load_file(path):
    with open(path, 'rb') as file:
        data = file.read()
    hsh = hashlib.sha256(data).hexdigest()
    return data, hsh


class Resources:
    "Resources used by rtools-gui"

    def __init__(self):
        self.__secure_firmware, self.__secure_firmware_hash = _load_file(SECURE_FIRMWARE)
        self.__uboot, self.__uboot_hash = _load_file(UBOOT)
        self.__rescue, self.__rescue_hash = _load_file(RESCUE)
        self.__dtb, self.__dtb_hash = _load_file(DTB)
        self.__hostname = socket.gethostname()

        curdir = os.getcwd()
        os.chdir(DIR_PREFIX)
        process = subprocess.run(
            ['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
        self.__rtools_head = process.stdout.decode(sys.getdefaultencoding()).strip()
        os.chdir(curdir)

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
    def rtools_head(self):
        "Git hash of rtools-gui repository HEAD"
        return self.__rtools_head
