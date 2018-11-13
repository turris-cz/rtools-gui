#!/usr/bin/env python3
from time import sleep
from rtools_gui.moxtester import MoxTester

def progress(value):
    print(value)

def main():
    mxt = MoxTester(3)
    mxt.selftest()
    mxt.reset_tester()

    if not mxt.board_present():
        print("Board not inserted")
        return

    mxt.power(True)
    print("SPI flash")
    with mxt.spiflash() as flash:
        flash.reset_device()
        with open('firmware/secure-firmware', 'rb') as file:
            data = file.read()
            flash.write(0x0, data, progress)
            if not flash.verify(0x0, data, progress):
                exit("SPI image verification failed")

    print("power up test")
    mxt.set_boot_mode(mxt.BOOT_MODE_SPI)
    mxt.power(True)
    mxt.reset(False)
    with mxt.uart() as uart:
        uart.expect(['Hit any key to stop autoboot'])
        uart.send('\n')
        uart.expect(['=>'])
        uart.send('help\n')
        uart.expect(['=>'])
    mxt.power(False)

    mxt.reset_tester()


main()
