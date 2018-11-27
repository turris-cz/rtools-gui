#!/usr/bin/env python3
from time import sleep
import argparse
from rtools_gui.moxtester import MoxTester


def progress(value):
    print(value)


def main():
    parser = argparse.ArgumentParser(prog="moxtester_serial")
    parser.add_argument('id', metavar='ID', type=int, nargs=1,
                        help='ID used to connect to moxtester')
    options = parser.parse_args()

    if options.id[0] < 0 or options.id[0] > 3:
        exit('ID should be 0 to 3')

    mxt = MoxTester(options.id[0])
    mxt.selftest()

    if not mxt.board_present():
        print("Board not inserted")
        return

    with mxt.spiflash() as flash:
        flash.reset_device()
        flash.chip_erase()


main()
