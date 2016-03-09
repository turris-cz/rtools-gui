#!/usr/bin/python

import sys

from PyQt5 import QtWidgets

from mainwindow import MainWindow

def main(argv):
    app = QtWidgets.QApplication(argv)
    mainwindow = MainWindow()
    mainwindow.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main(sys.argv)
