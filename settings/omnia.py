# database access
DB = dict(
    HOST='localhost',
    NAME='omnia_flashing',
    USER='omnia_flasher',
    PASSWORD='poiuytrewq',
)

# set the steps and tests modules
WORKFLOW_STEPS_MODULE = 'workflow.steps.omnia'
WORKFLOW_TESTS_MODULE = 'workflow.tests.omnia'

PATHS = {
    'sample': {
        'path': 'mock/sample.sh'
    },
    'bootloader_mcu': {
        'path': 'mock/sample.sh'
    },
    'omnia_hw_ctrl': {
        'path': 'mock/sample.sh'
    },
    'openocd_bin': {
        'path': 'mock/sample.sh'
    },
    'openocd_scripts': {
        'path': 'mock/'
    },
    'openocd_config': {
        'path': 'mock/sample.sh'
    },
    'uboot_flashing': {
        'path': 'mock/sample.sh'
    },
    'flashrom': {
        'path': 'mock/sample.sh'
    },
    'uboot_image': {
        'path': 'mock/sample.sh'
    },
    'atsha': {
        'path': 'mock/sample.sh'
    },
}

SERIAL_CONSOLE = {
    'tester': {
        'device': "/dev/ttyTESTER",
        'baudrate': 115200,
    },
    'router': {
        'device': "/dev/ttyROUTER",
        'baudrate': 115200,
    },
}

SPI_SPEED = 6000

ROUTER_RAMSIZE = 1  # only `1` or `2` (in GB)

LOG_APP_FILE = '/var/log/programmer/application.log'
LOG_ROUTERS_DIR = '/var/log/programmer/runs/'

import os
DB_RECOVER_QUERY_FILE = os.path.expanduser('~/recover-queries.json')

BACKUP_SCRIPT = 'backup_log.sh'
