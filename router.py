# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.

from persistent import Persistent

class Router(Persistent):
    STATUS_START = 0
    STATUS_I2C = 1
    STATUS_CPLD = 2
    STATUS_FINISHED = 3
    
    def __init__(self, id):
        self.id = id
        self.status = Router.STATUS_START
        self.error = ""

