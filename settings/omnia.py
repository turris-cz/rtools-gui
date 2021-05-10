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
WORKFLOW_STEPS_WORKSTATION_MODULE = 'workflow.steps.omnia_workstation_test'
WORKFLOW_TESTS_WORKSTATION_MODULE = 'workflow.tests.omnia'
DB_WRAPPER_MODULE = 'db_wrapper'
DB_WRAPPER_MOCK_MODULE = 'mock.db_wrapper'

PATHS = {
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

SPI_SPEED = 5000

ROUTER_RAMSIZE = 1  # only `1` or `2` (in GB)
REGION = '**'  # ** or iso country code (e.g. us)

LOG_ROUTERS_DIR = '/var/log/programmer/runs/'

import os
DB_RECOVER_QUERY_FILE = os.path.expanduser('~/recover-queries.json')

WORKSTATION_TESTING_SERIALS = [
    # Results of these serials won't be stored into the db
]

RERUN = 0

CHECK_STEPS_BEFORE_TESTS = True

CUSTOM_INIT_TITLE = None

FORCE_RESCAN_BARCODE = True

ALWAYS_STOP_ON_FAILURE = True

WATCHED_RUN_COUNT = 10

MODE_NAME = "NORMAL"
