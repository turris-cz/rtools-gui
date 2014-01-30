# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.

from PyQt4 import QtSql
import logging
from datetime import datetime
from os import path

logger = logging.getLogger('installer')

# in this file we write failed db queries - FIXME - it is a temporary solution
fdblog = path.join(path.split(path.abspath(__file__))[0],
                   "logdir/faileddbqueries")

CONN_ERR_MSG = u"Připojení k databázi selhalo. Zkontrolujte připojení k síti."


class DoesNotExist(IOError):
    pass


class DuplicateKey(IOError):
    pass


class DbError(IOError):
    pass


class Router(object):
    STATUS_START = 0
    STATUS_I2C = 1
    STATUS_CPLD = 2
    STATUS_UBOOT = 3
    STATUS_FINISHED = 4
    
    TEST_OK = 0
    TEST_FAIL = 1
    TEST_PROBLEM = 2
    
    def __init__(self, routerId):
        """Fetch the info about a router from db and if doesn't exist,
        raise DoesNotExist error"""
        
        self.id = routerId # string
        self.attempt = 0 # int
        self.status = Router.STATUS_START # int
        self.error = "" # string / text in db
        # second chance for flashing steps (if the user can check the cables)
        self.secondChance = {'I2C': True, 'CPLD': True, 'FLASH': True}
        self.testSerie = 0
        self.testResults = {}
        self.currentTest = 0
        
        # we use the default (and only) database, open it now if closed
        self.query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
    
    @classmethod
    def fetchFromDb(cls, routerId, attempt = -1):
        # attempt -1 means the last one
        routerId = str(routerId)
        
        if attempt == -1:
            subquery = "(SELECT max(attempt) FROM routers WHERE id = '%s')" % routerId.replace("'", "''")
        else:
            subquery = "'%d'" % attempt
        
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        if query.exec_("SELECT * FROM routers WHERE id = '%s' AND attempt = %s;"
                       % (routerId.replace("'", "''"), subquery)):
            if query.size() == 0:
                raise DoesNotExist()
            else:
                query.next()
                rec = query.record()
                
                router = cls(routerId)
                router.attempt = rec.value('attempt').toInt()[0]
                router.status = rec.value('status').toInt()[0]
                router.error = str(rec.value('error').toString())
        else:
            raise DbError(CONN_ERR_MSG)
        
        sqlquery = "SELECT MAX(serie) AS \"lastserie\" FROM tests WHERE id='%s' AND attempt='%d';" \
                   % (router.id.replace("'", "''"), router.attempt)
        if query.exec_(sqlquery):
            try:
                query.next()
                lastSerie = query.record().value("lastserie")
                router.testSerie = 0 if lastSerie.isNull() else lastSerie.toInt()[0] + 1
            except Exception:
                raise DbError(u"Chyba databáze, data nejsou v pořádku. Zkontrolujte integritu databáze.")
        else:
            logger.warning("[DB] fetching router max test serie failed (routerId=%s) with error\n%s"
                           % (router.id, str(query.lastError().text())))
            raise DbError(CONN_ERR_MSG)
        
        return router
    
    @classmethod
    def createNewRouter(cls, routerId):
        routerId = str(routerId)
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        if query.exec_("INSERT INTO routers (id) VALUES ('%s');" % routerId.replace("'", "''")):
            logger.debug("[DB] succesfully added router record (routerId=%s)" % routerId)
            return cls(routerId)
        elif str(query.lastError().text()).startswith("ERROR:  duplicate key"):
            raise DuplicateKey()
        else:
            raise DbError(CONN_ERR_MSG)
    
    @classmethod
    def nextAttempt(cls, routerId):
        routerId = str(routerId)
        query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database())
        if query.exec_("INSERT INTO routers (id, attempt, status) "
                       "SELECT '%(id)s' AS \"id\", attempt + 1 AS \"attempt\", status "
                       "FROM routers "
                       "WHERE id = '%(id)s' AND attempt = (SELECT max(attempt) FROM routers WHERE id = '%(id)s') "
                       "RETURNING attempt, status;"
                       % {'id': routerId.replace("'", "''")}):
            logger.debug("[DB] succesfully added router record (routerId=%s)" % routerId)
            router = cls(routerId)
            query.next()
            rec = query.record()
            router.attempt = rec.value('attempt').toInt()[0]
            router.status = rec.value('status').toInt()[0]
            return router
        elif str(query.lastError().text()).startswith("ERROR:  null value"):
            raise DoesNotExist()
        else:
            raise DbError(CONN_ERR_MSG)
    
    def save(self):
        # TODO be more precise, if no record with given id,...
        # and be consistent - raise a DbError if failure
        sqlquery = "UPDATE routers SET status='%d', error='%s' " \
                   "WHERE id='%s' AND attempt = '%d';" \
                   % (self.status, self.error.replace("'", "''"), self.id.replace("'", "''"), self.attempt)
        if self.query.exec_(sqlquery):
            logger.debug("[DB] succesfully updated router record (routerId=%s)" % self.id)
            return True
        else:
            logger.warning("[DB] router record update failed (routerId=%s)" % self.id)
            self.saveFailedDbQuery(sqlquery)
            return False
    
    def saveTestResult(self, testStatus, testText):
        sqlquery = "INSERT INTO tests (id, attempt, serie, testid, testresult, msg) " \
                   "VALUES ('%s', '%d', '%d', '%d', '%d', %s);" \
                   % (self.id.replace("'", "''"), self.attempt, self.testSerie, self.currentTest, testStatus,
                      "'%s'" % testText.replace("'", "''") if testStatus != 0 and testText else "NULL")
        if self.query.exec_(sqlquery):
            logger.debug("[DB] router test record inserted successfully (routerId=%s)" % self.id)
            return True
        else:
            logger.warning("[DB] router test record insertion failed (routerId=%s)" % self.id)
            self.saveFailedDbQuery(sqlquery)
            return False
    
    def saveFailedDbQuery(self, sqlQuery):
        # FIXME do this better, inform the user about db failure
        # save to file
        try:
            with open(fdblog, "a") as fh:
                fh.write(str(datetime.now()) + "\n" + sqlQuery + "\n\n")
        except Exception:
            pass
