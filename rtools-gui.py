#!/usr/bin/python

import sys

from application import Application
from guard import Guard

def main(argv):

    with Guard():
        app = Application(argv)

        # this import need to be used after the app is created
        from mainwindow import MainWindow

        mainwindow = MainWindow()
        mainwindow.show()
        retval = app.exec_()

    sys.exit(retval)


if __name__ == '__main__':
    main(sys.argv)
