# coding=utf-8

# this file defines tests which are run after successful flashing
# it is a tuple of tests, each of which contains description for
# a person executing the tests and second is a function which takes
# SerialConsole object and executest the tests
# a test can yield -1 - unparsable command output
#                  >=0 - result of the test


import subprocess
from shlex import split

import os
import importlib

settings_module = os.environ.get('RTOOLS_SETTINGS', 'settings')
settings = importlib.import_module(settings_module)


# results from
#     runLocalCmd
#     runRemoteCmd
#     test_*
#     are in the form
#     (
#         int exit_status (-1 if not a number),
#         str exit_status,
#         str command_output,
#         str ("Local cmd:\n" | "Remote cmd\n:" + command)
#    )


def runLocalCmd(cmdstr):
    p = subprocess.Popen(split(cmdstr), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    retCode = p.wait()
    stdOut = p.stdout.read()
    return (retCode, str(retCode), stdOut, "Local cmd:\n" + cmdstr)


def runRemoteCmd(sc, cmdstr):
    stdOut = sc.exec_(cmdstr)
    cmdStatus = sc.lastStatus()
    intCmdStatus = int(cmdStatus) if cmdStatus.isdigit() else -1
    return (intCmdStatus, cmdStatus, stdOut, "Remote cmd:\n" + cmdstr)


def textresult_generic(p_result):
    return "%s<br>returned:<br>%s<br>return code: %s" % (
        p_result[3], p_result[2], p_result[1]
    )
