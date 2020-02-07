# -*- coding: utf8 -*-

from omnia_offline import *

SERIAL_CONSOLE['router']['device'] = '/dev/ttyTESTS'
# tester should not be used in this phase so it can be mocked
SERIAL_CONSOLE['tester']['mock'] = 'mock/sc_pipe_tester_mock.py'

LOG_APP_FILE = '/var/log/programmer/application-tests.log'


WORKFLOW_TESTS_MODULE = 'workflow.tests.omnia_distributors'

# In case that the distributor's db is separated from the production
CHECK_STEPS_BEFORE_TESTS = False

CUSTOM_INIT_TITLE = u'Testování u distirbutorů'
