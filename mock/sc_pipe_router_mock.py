#!/usr/bin/env python2

from sc_pipe_mock import runMain

PLAN = {
    'ls': [
        (1000, ".\n"),
    ],
    'echo "###$?###"': [
        (2000, '###0###\n'),
    ],
}


if __name__ == '__main__':
    runMain(PLAN)
