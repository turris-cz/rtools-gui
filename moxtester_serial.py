#!/usr/bin/env python3
import os
import sys
import fcntl
import argparse
import atexit
import select
import termios
import tty
from rtools_gui.moxtester import MoxTester


EXIT_SEQ = ("\r~.").encode('utf-8')
exit_seq_progress = 0


def detect_escseq(data):
    "Detect exit sequence in data stream"
    global exit_seq_progress
    for byte in data:
        if byte == EXIT_SEQ[exit_seq_progress]:
            exit_seq_progress = exit_seq_progress + 1
            if exit_seq_progress >= len(EXIT_SEQ):
                return True
        else:
            exit_seq_progress = 0
            if byte == EXIT_SEQ[0]:
                exit_seq_progress = exit_seq_progress + 1
    return False


def cleanup(mxt, stdin_tio_back):
    "At exit cleanup function"
    mxt.default()
    if stdin_tio_back is not None:
        termios.tcsetattr(0, termios.TCSANOW, stdin_tio_back)


def main():
    parser = argparse.ArgumentParser(prog="moxtester_serial")
    parser.add_argument('id', metavar='ID', type=int, nargs=1,
                        help='ID used to connect to moxtester')
    options = parser.parse_args()

    if options.id[0] < 0 or options.id[0] > 3:
        exit('ID should be 0 to 3')

    # Create mox tester
    mxt = MoxTester(options.id[0])
    mxt.connect_tester()
    if not mxt.board_present():
        print("Board not inserted", file=sys.stderr)
        sys.exit(1)

    # Backup current stdin configuration
    stdin_tio_back = None
    if sys.stdin.isatty():
        stdin_tio_back = termios.tcgetattr(0)

    # Register cleanup
    atexit.register(cleanup, mxt, stdin_tio_back)

    # Configure FD for UART
    fileno = mxt.uart_fileno()
    curfcntl = fcntl.fcntl(fileno, fcntl.F_GETFL, 0)
    fcntl.fcntl(
        fileno, fcntl.F_SETFL,
        curfcntl & os.O_NONBLOCK & (os.O_NDELAY ^ 0xffffffff))
    # Configure FD for stdin
    if stdin_tio_back is not None:
        tty.setraw(0, termios.TCSANOW)

    poll = select.poll()
    poll.register(fileno, select.POLLIN)
    poll.register(0, select.POLLIN)

    mxt.power(True)
    mxt.reset(False)

    print("Use '<Enter>~.' sequence to exit.", end='\n\r', file=sys.stderr)
    while True:
        pfds = poll.poll()
        for pfd in pfds:
            data = os.read(pfd[0], 4096)
            if not data:  # EOF
                return
            if pfd[0] == 0 and detect_escseq(data):
                return
            written = os.write(0 if pfd[0] != 0 else fileno, data)
            if written != len(data):
                print("Not all data written!", file=sys.stderr)
                sys.exit(2)


if __name__ == '__main__':
    main()
