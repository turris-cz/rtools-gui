from logging import NOTSET as _NOTSET

# commands
# OPENOCD_CMD = "/usr/bin/openocd"
# STEP_I2C_CMD = "/home/turris/remote_run.sh"
# STEP_CPLD_CMD = "/usr/local/programmer/3.0_x64/bin/lin64/pgrcmd"
# CPLD_FLASH_INFILE = "/home/turris/workspace_cpld/cpld/CZ_NIC_Router_CPLD_program.xcf"
# CPLD_ERASE_INFILE = "/home/turris/workspace_cpld/cpld/CZ_NIC_Router_CPLD_erase.xcf"
# STEP_FLASH_CMD = "/home/turris/workspace/go_TURRIS_UBOOT_program.sh"
# STEP_FLASH_LOGFILE = "/home/turris/workspace/session.log"
# LOG_BACKUP_CMD = "/home/turris/backup_logs.sh"

STEP_I2C_CMD = "mock/i2cflasher"
STEP_CPLD_CMD = "mock/lattice"

OPENOCD_CMD = "mock/openocd"
OPENOCD_DIR = "/usr/share/openocd/scripts"
OPENOCD_INTERFACE = "stlink-v2.cfg"
OPENOCD_TARGET = "stm32f0x_stlink.cfg"
POWER_BIN = "mock/turris_power_control.bin"

CPLD_FLASH_INFILE = "/home/palko/neexistujucialejetojedno"
CPLD_ERASE_INFILE = "/home/palko/neexistujucialejetojedno"
LOG_BACKUP_CMD = "/bin/true"

# database
# DB_HOST = "10.0.0.2"
DB_HOST = 'localhost'
DB_USER = 'tflasher'
DB_PASS = 'poiuytrewq'
DB_DBNAME = 'tflasher'

#logging
LOGLEVEL = _NOTSET  # log everyting
LOGFILE = "logdir/flasher.log"
LOGFORMAT = '%(asctime)s - %(levelname)s - %(message)s'
FLASH_LOGS = "nandnorlogs"

LOCAL_TEST_IFACE = "eth42"
TURRIS_WAN_IFACE = "eth2"

PS1_OVERRIDE = "root@OpenWrt:/# "
