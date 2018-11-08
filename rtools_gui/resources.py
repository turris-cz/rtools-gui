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

secure_firmware = None  # Bytes of secure firmware
secure_firmware_hash = None  # sha256sum of secure firmware
uboot = None  # Bytes of u-boot
uboot_hash = None  # sha256sum of u-boot hash
rescue = None  # Bytes of rescue image
rescue_hash = None  # sha256sum of rescue image
dtb = None  # Bytes of device tree
dtb_hash = None  # sha256sum of device tree
rtools_head = None  # Git hash of HEAD
hostname = None  # Hostname of host machine


def __load_file(path):
    with open(path, 'rb') as file:
        data = file.read()
    hsh = hashlib.sha256(data).hexdigest()
    return data, hsh


def load_resources():
    "Load resources to this module"
    global secure_firmware, secure_firmware_hash
    secure_firmware, secure_firmware_hash = __load_file(SECURE_FIRMWARE)
    global uboot, uboot_hash
    uboot, uboot_hash = __load_file(UBOOT)
    global rescue, rescue_hash
    rescue, rescue_hash = __load_file(RESCUE)
    global dtb, dtb_hash
    dtb, dtb_hash = __load_file(DTB)
    global rtools_head
    curdir = os.getcwd()
    os.chdir(DIR_PREFIX)
    process = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
    rtools_head = process.stdout.decode(sys.getdefaultencoding()).strip()
    os.chdir(curdir)
    global hostname
    hostname = socket.gethostname()
