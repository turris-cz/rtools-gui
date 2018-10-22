#!/usr/bin/env python3
import argparse
import ftdi1 as ftdi


def main():
    parser = argparse.ArgumentParser(prog="moxtester_burn_id")
    parser.add_argument('id', metavar='ID', type=int, nargs=1,
                        help='Id to be burned to moxtester')
    options = parser.parse_args()

    if options.id[0] <= 0 or options.id[0] > 4:
        exit('ID should be 1 to 4')

    ctx = ftdi.new()
    ret, devs = ftdi.usb_find_all(ctx, 0x0403, 0x6011)
    if ret < 0:
        exit("Unable to list USB devices")
    if devs is None:
        exit('There is no connected compatible FTDI device')
    if devs.next is not None:
        exit('Multiple FTDI devices connected. Please connect only one')

    if ftdi.usb_open_dev(ctx, devs.dev) != 0:
        exit('Unable to open FTDI device')

    if ftdi.read_eeprom(ctx) < 0:
        exit('EEPROM read failed')
    if ftdi.eeprom_decode(ctx, 1):
        exit('EEPROM decode failed')

    ret, type_val = ftdi.get_eeprom_value(ctx, ftdi.CHIP_TYPE)
    if ret < 0:
        exit('Unable to read value from EEPROM')

    if type_val > 0 and type_val < 4:
        print('Connected Mox Tester seems to have valid ID: ' + str(type_val))
        input("Press Enter to continue...")

    if ftdi.set_eeprom_value(ctx, ftdi.CHIP_TYPE, options.id[0]) < 0:
        exit("EEPROM value write failed")
    if ftdi.eeprom_build(ctx) < 0:
        exit('EEPROM build (write) failed')
    if ftdi.write_eeprom(ctx) < 0:
        exit('EEPROM write failed')

    print('ID of connected Mox Tester set to: ' + str(options.id[0]))


if __name__ == '__main__':
    main()
