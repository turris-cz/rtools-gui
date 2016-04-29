#!/usr/bin/python

import sys
import argparse

from application import Application
from guard import Guard


def main(argv):

    parser = argparse.ArgumentParser(prog="rtools-gui")
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-t", "--tests-only", dest='tests', default="", action='store_const', const='test',
        help='tests only'
    )
    group.add_argument(
        "-s", "--steps-only", dest='steps', default="", action='store_const', const='step',
        help='steps only'
    )
    options = parser.parse_args()

    with Guard(options.steps + options.tests):
        app = Application(argv)

        # this import need to be used after the app is created
        from mainwindow import MainWindow

        mainwindow = MainWindow()
        mainwindow.show()
        retval = app.exec_()

    sys.exit(retval)


if __name__ == '__main__':
    main(sys.argv)
