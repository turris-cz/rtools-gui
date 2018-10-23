#!/usr/bin/env python3
from time import sleep
from moxtester import MoxTester


def main():
    mxt = MoxTester(1)
    mxt.selftest()

    if not mxt.board_present():
        print("Board not inserted")
        return

    print("SPI flash")
    with mxt.spiflash() as flash:
        flash.reset_device()
        with open('untrusted-flash-image.bin', 'rb') as file:
            data = file.read()[0:1 << 16]
            flash.write(0x0, data)
            if not flash.verify(0x0, data):
                exit("SPI image verification failed")
    return

    print("power up test")
    mxt.set_boot_mode(mxt.BOOT_MODE_SPI)
    mxt.power(True)
    with mxt.uart() as uart:
        mxt.reset(False)
        uart.expect(['Hit any key to stop autoboot'])
        uart.send('\n')
        uart.expect(['=>'])
        uart.send('help\n')
        uart.expect(['=>'])
    mxt.power(False)


main()
