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

SCRIPTS = {
    'sample': {
        'script_path': 'mock/sample.sh'
    }
}

SERIAL_CONSOLE = {
    'tester': {
        'device': "/dev/ttyTESTER",
        'baudrate': 115200,
        'mock': 'mock/sc_pipe_tester_mock.py',  # TODO remove before deploying
    },
    'router': {
        'device': "/dev/ttyROUTER",
        'baudrate': 115200,
    },
}

LOG_APP_FILE = '/var/log/programmer/application.log'
LOG_ROUTERS_DIR = '/var/log/programmer/runs/'

import os
DB_RECOVER_QUERY_FILE = os.path.expanduser('~/recover-queries.json')

BACKUP_SCRIPT = 'backup_log.sh'
