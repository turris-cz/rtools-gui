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
    print(mxt.power_supply_ok())
    mxt.power(True)
    st = False
    while True:
        print(st)
        mxt.reset(st)
        st = not st
        sleep(5)
    mxt.power(False)


main()
