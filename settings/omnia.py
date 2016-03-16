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

STEP_SETTINGS = {
    'sample': {
        'script_path': 'mock/sample.sh'
    }
}

SERIAL_CONSOLE_SETTINGS = {
    'device': "/dev/ttyUSB0",
    'baudrate': 115200,
}

LOG_APP_FILE = '/tmp/rtools/application.log'
LOG_ROUTERS_DIR = '/tmp/rtools/outputs/'
