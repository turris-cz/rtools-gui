#!/usr/bin/python

from sc_pipe_mock import runMain

PLAN = {
    'SETINIT': [
        (100, "."),
        (200, "."),
        (300, "."),
        (400, "."),
        (500, "."),
        (600, "."),
        (700, "."),
        (800, "."),
        (900, "."),
        (1000, "."),
        (1100, "OK\n"),
    ],
    'PWRUP': [
        (1, "."),
        (2, "."),
        (3, "."),
        (4, "."),
        (5, "."),
        (6, "."),
        (7, "."),
        (8, "."),
        (9, "."),
        (10, "."),
        (11, "OK\n"),
    ],
    'PROGRAM': [
        (100, ".."),
        (300, ".."),
        (500, ".."),
        (700, ".."),
        (900, ".."),
        (1100, "OK\n"),
    ],
    'RSV': [
        (100, "...."),
        (500, "...."),
        (900, ".."),
        (1100, "OK\n"),
    ],
    'PWRDOWN': [
        (100, "........"),
        (900, ".."),
        (1100, "OK\n"),
    ],
    'HWSTART': [
        (100, "........"),
        (900, "..OK\n"),
    ],
    'RESETALL': [
        (100, "Tester reset\n---OMNIA TESTER---\r\n"),
    ],
    'RESETDUT': [
        (1, "..........OK\n"),
    ],
    'CPUOFF': [
        (1, "..........OK\n"),
    ],
    'CPUON': [
        (1, "..........OK\n"),
    ],
    'MCUOFF': [
        (1, "..........OK\n"),
    ],
    'MCUON': [
        (1, "..........OK\n"),
    ],
    'STATUS': [
        (1, "..........OK\n"),
    ],
    'SELFTEST': [
        (1, "..........OK\n"),
    ],
}


if __name__ == '__main__':
    runMain(PLAN)
