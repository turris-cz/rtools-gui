from omnia import *

SERIAL_CONSOLE['router']['device'] = '/dev/ttyTESTS'
# tester should not be used in this phase so it can be mocked
SERIAL_CONSOLE['tester']['mock'] = 'mock/sc_pipe_tester_mock.py'
