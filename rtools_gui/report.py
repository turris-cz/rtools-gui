import sys


def fail_exit(message, exit_code=1):
    "Report message and exit with given exit_code"
    print(message, file=sys.stderr)
    sys.exit(exit_code)
