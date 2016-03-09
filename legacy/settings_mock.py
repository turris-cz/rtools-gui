from logging import NOTSET as _NOTSET

# commands
STEP_I2C_CMD = "mock/i2cflasher"
STEP_CPLD_CMD = "mock/lattice"

OPENOCD_CMD = "mock/openocd"
OPENOCD_DIR = "/usr/share/openocd/scripts"
OPENOCD_INTERFACE = "stlink-v2.cfg"
OPENOCD_TARGET = "stm32f0x_stlink.cfg"
POWER_BIN = "mock/turris_power_control.bin"

CPLD_FLASH_INFILE = "/path/to/file"
CPLD_ERASE_INFILE = "/path/to/file"
LOG_BACKUP_CMD = "/bin/true"

# database
DB_HOST = 'localhost'
DB_USER = 'tflasher'
DB_PASS = 'poiuytrewq'
DB_DBNAME = 'turris'

#logging
LOGLEVEL = _NOTSET  # log everyting
LOGFILE = "logdir/flasher.log"
LOGFORMAT = '%(asctime)s - %(levelname)s - %(message)s'
FLASH_LOGS = "nandnorlogs"

LOCAL_TEST_IFACE = "eth42"
TURRIS_WAN_IFACE = "eth2"

# Error cases
#STEP_I2C_CMD = "/bin/false"
#STEP_CPLD_CMD = "/bin/false"
#OPENOCD_CMD = "/bin/false"
