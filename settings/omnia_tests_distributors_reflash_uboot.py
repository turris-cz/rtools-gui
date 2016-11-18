# -*- coding: utf8 -*-

from omnia_tests_distributors import *

# Don't open the serial port only local commands are used here
SERIAL_CONSOLE['router']['mock'] = 'mock/sc_pipe_tester_mock.py'

WORKFLOW_TESTS_MODULE = 'workflow.tests.omnia_distributors_reflash_uboot'

PATHS['uboot_reflash'] = {
    'tty': '/dev/ttyTESTS',
    'beacon': '/usr/local/bin/sendbeacon',
    'kwboot': '/usr/local/bin/kwboot',
    'uart_uboot': '/home/pi/programmer/uboot-turris-omnia-uart-spl.kwb',
    'load_script': '/usr/local/sbin/load_uboot.sh',
    'write_script': '/usr/local/sbin/rewrite_uboot.sh',
    'img_file': '/home/pi/programmer/uboot-turris-omnia.img',
}

REFLASH = {
    'router_ip': '192.168.160.100',
    'server_ip': '192.168.160.1',
}


LOG_APP_FILE = '/var/log/programmer/application-reflash-uboot.log'

CUSTOM_INIT_TITLE = u'Aktualizace bootloaderu'
