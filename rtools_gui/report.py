import sys


def fail_exit(message, exit_code=1):
    "Report message and exit with given exit_code"
    print("Fatal: " + str(message), file=sys.stderr)
    sys.exit(exit_code)


def error(message):
    "Print error message"
    print("Error: " + str(message), file=sys.stderr)
