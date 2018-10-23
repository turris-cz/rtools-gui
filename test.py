#!/usr/bin/env python3
from time import sleep
from moxtester import MoxTester

# with open('test', 'r') as file:
#fd = fdpexpect.fdspawn(file)
#print(fd.expect(['->', 'test']))

def main():
    mxt = MoxTester(1)
    mxt.selftest()

    #print(hex(mxt._b.gpio_value))
    #for _ in range(5):
    #    mxt._b.set(False, 0x08)
    #    print(hex(mxt._b.gpio_value))
    #    sleep(0.1)
    #    mxt._b.set(True, 0x08)
    #    print(hex(mxt._b.gpio_value))
    #    sleep(0.1)
    #return

    #mxt.power(True)
    #spi = mxt._b
    #spi.spi_enable(True)
    #while True:
    #    print(hex(spi.spi_burst((
    #        (spi.SPI_SWAP, 1, 0x42),
    #        ))))
    #    sleep(1)

    if not mxt.board_present():
        print("Board not inserted")
        return

    #mxt.power(True)
    #with mxt.uart() as uart:
        #mxt.set_boot_mode(mxt.BOOT_MODE_SPI)
        #mxt.reset(False)
        #uart.expect(['Hit any key to stop autoboot'])
        #uart.send('\n')
        #uart.expect(['=>'])
        #uart.send('help\n')
        #uart.expect(['=>'])

    mxt.set_boot_mode(mxt.BOOT_MODE_UART)

    with mxt.spiflash() as flash:
        flash.reset_device()
        print(hex(flash.jedec_id()))
        print(flash.read_data(0x00, 256))

    mxt.power(False)


main()
