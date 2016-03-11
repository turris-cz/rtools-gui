import re

from PyQt5 import QtSql
from application import qApp

from custom_exceptions import DbError

class Router(object):

    @staticmethod
    def executeQuery(sql, *values):
        query = QtSql.QSqlQuery(qApp.connection.database())
        if not query.prepare(sql):
            raise DbError("Wrong sql '%s'" % sql)

        for value in values:
            query.addBindValue(value)

        # TODO logging db goes here
        print re.sub(' +', ' ', re.sub('\n', ' ', query.executedQuery())).strip(), values
        if not query.exec_():
            raise DbError(qApp.connection.lastError().text())

        return query

    def startRun(self):
        sql = "INSERT INTO runs (router) VALUES (?) RETURNING id;"
        query = self.executeQuery(sql, self.id)
        query.first()
        self.currentRun = query.record().value('id')
        # TODO log run

    def createIfNeeded(self):
        sql = "SELECT * FROM routers WHERE id = ?;"
        query = Router.executeQuery(sql, self.id)
        if query.size() == 0:
            # Insert record
            sql = "INSERT INTO routers (id) VALUES (?);"
            Router.executeQuery(sql, self.id)
            return True
        return False

    def loadSteps(self):
        sql = """ SELECT DISTINCT steps.step_name AS name, steps.passed as passed from routers
                  INNER JOIN runs ON runs.router = routers.id
                  INNER JOIN steps ON runs.id = steps.run
                  WHERE routers.id = ?;
              """
        query = Router.executeQuery(sql, self.id)
        self.performedSteps = dict(failed=set(), passed=set())
        while query.next():
            # TODO logging
            print query.record().value('name'), query.record().value('passed')
            if query.record().value('passed'):
                self.performedSteps['passed'].add(query.record().value('name'))
            else:
                self.performedSteps['failed'].add(query.record().value('name'))

    def incStepAttempt(self):
        self.stepAttempt += 1

    def incTestAttempt(self):
        self.testAttempt += 1

    def storeStep(self, name, passed):
        sql = """ INSERT INTO steps (run, step_name, step_order, attempt, passed)
                  VALUES (?, ?, ?, ?, ?);
              """
        order = len(self.performedSteps['passed'])
        Router.executeQuery(sql, self.currentRun, name, order, self.stepAttempt, passed)

    def storeTest(self, name, passed):
        sql = """ INSERT INTO tests (run, test_name, attempt, result)
                  VALUES (?, ?, ?, ?);
              """
        Router.executeQuery(sql, self.currentRun, name, self.stepAttempt, passed)

    def __init__(self, routerId):
        self.performedSteps = dict(failed=set(), passed=set())
        self.id = str(routerId).strip()
        self.stepAttempt = 0
        self.testAttempt = 0

        # create db record if needed
        if not self.createIfNeeded():
            # When the router is not created get steps which passed
            self.loadSteps()

        # everytime the record is loaded start a new run
        self.startRun()
