#!/usr/bin/python

from sc_pipe_mock import runMain

PLAN = {
    'ls': [
        (1000, "."),
    ],
    'echo "###$?###"': [
        (2000, '###0###'),
    ],
}


if __name__ == '__main__':
    runMain(PLAN)
