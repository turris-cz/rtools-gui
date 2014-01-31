from logging import NOTSET as _NOTSET

# commands
# STEP_I2C_CMD = "/home/turris/remote_run.sh"
# STEP_CPLD_CMD = "/usr/local/programmer/3.0_x64/bin/lin64/pgrcmd"
# CPLD_FLASH_INFILE = "/home/turris/workspace_cpld/cpld/CZ_NIC_Router_CPLD_program.xcf"
# CPLD_ERASE_INFILE = "/home/turris/workspace_cpld/cpld/CZ_NIC_Router_CPLD_erase.xcf"
# STEP_FLASH_CMD = "/home/turris/workspace/go_TURRIS_UBOOT_program.sh"
# STEP_FLASH_LOGFILE = "/home/turris/workspace/session.log"
# LOG_BACKUP_CMD = "/home/turris/backup_logs.sh"
STEP_I2C_CMD = "/home/palko/Projects/router/instalator/mock/i2cflasher"
STEP_CPLD_CMD = "/home/palko/Projects/router/instalator/mock/lattice"
CPLD_FLASH_INFILE = "/home/palko/neexistujucialejetojedno"
CPLD_ERASE_INFILE = "/home/palko/neexistujucialejetojedno"
STEP_FLASH_CMD = "/home/palko/Projects/router/instalator/mock/codewarrior"
STEP_FLASH_LOGFILE = "/home/palko/Projects/router/instalator/mock/session.log"
LOG_BACKUP_CMD = "/bin/true"

# database
# DB_HOST = "10.0.0.2"
DB_HOST = 'localhost'
DB_USER = 'tflasher'
DB_PASS = 'poiuytrewq'
DB_DBNAME = 'turris'

#logging
LOGLEVEL = _NOTSET # log everyting
LOGFILE = "logdir/flasher.log"
LOGFORMAT = '%(asctime)s - %(levelname)s - %(message)s'
FLASH_LOGS = "nandnorlogs"

LOCAL_TEST_IFACE = "eth42"
TURRIS_WAN_IFACE = "eth2"

TFTP_IMAGE_FILE = "/home/palko/Projects/router/instalator/dbinit.sql"
# TFTP_IMAGE_FILE = "/home/turris/workspace/tftp/nor.bin"
