from logging import NOTSET as _NOTSET

# commands
OPENOCD_CMD = "/usr/local/bin/openocd-wrapper"
OPENOCD_INTERFACE = "sysfsgpio-raspberrypi.cfg"
OPENOCD_TARGET = "stm32f0x.cfg"
OPENOCD_DIR = "/usr/local/share/openocd/scripts"
POWER_BIN = "/home/pi/turris_power_control.bin"

STEP_I2C_CMD = "/home/pi/jachym/remote_run.sh"

STEP_CPLD_CMD = "/usr/local/bin/jtag"
CPLD_FLASH_CMDS_FILE = "/home/pi/turris_cpld/urjtag_cmds"
#CPLD_ERASE_INFILE = "/home/turris/workspace_cpld/cpld/CZ_NIC_Router_CPLD_erase.xcf"

STEP_FLASH_LOGFILE = "/home/turris/workspace/session.log"
LOG_BACKUP_CMD = "/home/turris/backup_logs.sh"


#STEP_I2C_CMD = "mock/i2cflasher"
#STEP_CPLD_CMD = "mock/lattice"
#OPENOCD_CMD = "mock/openocd"
#OPENOCD_DIR = "/usr/share/openocd/scripts"
#OPENOCD_INTERFACE = "stlink-v2.cfg"
#OPENOCD_TARGET = "stm32f0x_stlink.cfg"
#POWER_BIN = "mock/turris_power_control.bin"
#CPLD_FLASH_INFILE = "/home/palko/neexistujucialejetojedno"
#CPLD_ERASE_INFILE = "/home/palko/neexistujucialejetojedno"
#LOG_BACKUP_CMD = "/bin/true"

# database
# DB_HOST = "10.0.0.2"
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
