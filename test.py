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

    mxt.set_boot_mode(mxt.BOOT_MODE_UART)
    mxt.power(True)
    with mxt.uart() as uart:
        uart.expect(['Hit any key to stop autoboot'])
        uart.send('\n')
        uart.expect(['=>'])
        uart.send('help\n')
        sleep(1)
    mxt.power(False)
    return


main()
