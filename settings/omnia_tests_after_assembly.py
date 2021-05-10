# -*- coding: utf8 -*-
from omnia import *

SERIAL_CONSOLE['router']['device'] = '/dev/ttyTESTS'
# tester should not be used in this phase so it can be mocked
SERIAL_CONSOLE['tester']['mock'] = 'mock/sc_pipe_tester_mock.py'

WORKFLOW_TESTS_MODULE = 'workflow.tests.omnia_after_assembly'
WORKFLOW_TESTS_WORKSTATION_MODULE = 'workflow.tests.omnia_after_assembly'

MODE_NAME = "PO SESTAVENÍ"
