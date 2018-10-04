#!/usr/bin/env python3
from time import sleep
from moxtester import MoxTester

# with open('test', 'r') as file:
#fd = fdpexpect.fdspawn(file)
#print(fd.expect(['->', 'test']))

def main():
    mxt = MoxTester(0)

    if not mxt.board_present():
        print("Board not inserted")
        return

    mxt.power(True)
    with mxt.uart() as uart:
        mxt.set_boot_mode(mxt.BOOT_MODE_SPI)
        mxt.reset(False)
        uart.expect(['Hit any key to stop autoboot'])
        uart.send('\n')
        uart.expect(['=>'])
        uart.send('help\n')
        sleep(1)
        mxt.reset(True)
        mxt.set_boot_mode(mxt.BOOT_MODE_UART)
        mxt.reset(False)
        sleep(5)
    mxt.power(False)
    return

    mxt.power(True)
    mxt.reset(False)
    while True:
        mxt.set_boot_mode(mxt.BOOT_MODE_SPI)
        print("spi")
        sleep(3)
        mxt.set_boot_mode(mxt.BOOT_MODE_UART)
        print("uart")
        sleep(3)


main()
