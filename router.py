# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.

from PyQt4 import QtSql
import logging

logger = logging.getLogger('installer')

CONN_ERR_MSG = u"Připojení k databázi zlyhalo. Zkontrolujte připojení k síti."


class DoesNotExist(IOError):
    pass


class DbError(IOError):
    pass


class Router(object):
    STATUS_START = 0
    STATUS_I2C = 1
    STATUS_CPLD = 2
    STATUS_FINISHED = 3
    
    def __init__(self, id, readonly=False):
        """Fetch the info about a router from db and if doesn't exist and readonly=False,
        create the new router and initialize it with default values"""
        
        self.id = id # string
        self.status = Router.STATUS_START # int
        self.error = "" # string / text in db
        
        # we use the default (and only) database, open it now if closed
        self.query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        
        if self.query.exec_("SELECT * FROM routers WHERE id='%s';" % self.id):
            if self.query.size() == 0:
                if readonly:
                    raise DoesNotExist()
                
                # no record, add
                if self.query.exec_("INSERT INTO routers VALUES ('%s', '%d', '');" %
                                    (self.id, self.status)):
                    logger.debug("[DB] succesfully added new router (routerId=%s)" % self.id)
                else:
                    # TODO handle duplicate key error
                    logger.warning("[DB] failed to add new router (routerId=%s)" % self.id)
                    raise DbError(CONN_ERR_MSG)
            else:
                # TODO do this better using name of column
                self.query.next()
                self.status = self.query.value(1).toInt()[0]
                self.error = self.query.value(2).toString()
                
        else:
            raise DbError(CONN_ERR_MSG)
    
    def save(self):
        # TODO be more precise, if no record with given id,...
        # and be consistent - raise a DbError if failure
        if self.query.exec_("UPDATE routers SET status='%d', error='%s' WHERE id='%s';" %
                            (self.status, self.error, self.id)):
            logger.debug("[DB] succesfully updated router record (routerId=%s)" % self.id)
            return True
        else:
            logger.debug("[DB] router record update failed (routerId=%s)" % self.id)
            return False
