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
    
    def __init__(self, routerId):
        """Fetch the info about a router from db and if doesn't exist,
        raise DoesNotExist error"""
        
        self.id = routerId # string
        self.attempt = 0 # int
        self.status = Router.STATUS_START # int
        self.error = "" # string / text in db
        # second chance for flashing steps (if the user can check the cables)
        self.secondChance = {'I2C': True, 'CPLD': True, 'FLASH': True}
        
        # we use the default (and only) database, open it now if closed
        self.query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
    
    @classmethod
    def fetchFromDb(cls, routerId, attempt = -1):
        # attempt -1 means the last one
        routerId = str(routerId)
        
        if attempt == -1:
            subquery = "(SELECT max(attempt) FROM routers WHERE id = '%s')" % routerId
        else:
            subquery = "'%d'" % attempt
        
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        if query.exec_("SELECT * FROM routers WHERE id = '%s' AND attempt = %s;"
                       % (routerId, subquery)):
            if query.size() == 0:
                raise DoesNotExist()
            else:
                query.next()
                rec = query.record()
                
                router = cls(routerId)
                router.attempt = rec.value('attempt').toInt()[0]
                router.status = rec.value('status').toInt()[0]
                router.error = str(rec.value('error').toString())
                return router
        else:
            raise DbError(CONN_ERR_MSG)
    
    @classmethod
    def createNewRouter(cls, routerId):
        routerId = str(routerId)
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        if query.exec_("INSERT INTO routers (id) VALUES ('%s');" % routerId):
            return cls(routerId)
        else:
            raise DbError(CONN_ERR_MSG)
    
    def nextAttempt(self):
        if self.query.exec_("INSERT INTO routers (id, attempt) VALUES ('%s', '%d');"
                            % (self.id, self.attempt + 1)):
            router = Router(self.id)
            router.attempt = self.attempt + 1
            return router
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
