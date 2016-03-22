import re
import json

from PyQt5 import QtSql
from application import qApp, tests, workflow, settings

from custom_exceptions import DbError


def writeRecovery(sql, *values):
    # Read the recovery file
    try:
        with open(settings.DB_RECOVER_QUERY_FILE) as f:
            jsonData = json.load(f)
    except IOError:
        # file probably doesn't exists
        jsonData = []

    jsonData.append([sql, values])

    # Store data
    # if it fails exception will be raised and program quits
    with open(settings.DB_RECOVER_QUERY_FILE, 'w') as f:
        json.dump(jsonData, f)
        f.flush()

def restoreRecovery():

    try:
        with open(settings.DB_RECOVER_QUERY_FILE) as f:
            jsonData = json.load(f)
    except IOError:
        # file probably doesn't exists no restore needed
        return

    if not jsonData:
        # nothing to restore
        return

    qApp.loggerMain.info("Starting to perform recovery queries.")

    for sql, values in jsonData:

        queryText = "%s %s" % \
            (re.sub(' +', ' ', re.sub('\n', ' ', sql)).strip(), values)

        query = QtSql.QSqlQuery(qApp.connection.database())
        if not query.prepare(sql):
            qApp.loggerDb.error("Recovery query failed '%s'" % queryText)
            raise DbError("Failed to perform a recovery query.")

        for value in values:
            query.addBindValue(value)

        if not query.exec_():
            qApp.loggerDb.error("Recovery query failed '%s'" % queryText)
            raise DbError(qApp.connection.lastError().text())

        qApp.loggerDb.info("Recovery query passed '%s'" % queryText)

    # Store data empty list
    with open(settings.DB_RECOVER_QUERY_FILE, 'w') as f:
        json.dump([], f)
        f.flush()

    qApp.loggerMain.info("All queries recovered.")

class Router(object):

    @property
    def idHex(self):
        return "%016x" % int(self.id)

    def __init__(self, routerId):
        self.performedSteps = dict(failed=set(), passed=set())
        self.id = str(routerId).strip()
        self.stepAttempt = 0
        self.testAttempt = 0
        self.dbFailed = False

        # create db record if needed
        if not self.createIfNeeded():
            # When the router is not created get steps which passed
            self.loadSteps()

        # everytime the record is loaded start a new run
        self.startRun()

    def executeQuery(self, sql, *values, **kwargs):
        failOnError = kwargs.get('failOnError', True)

        queryText = "%s %s" % \
            (re.sub(' +', ' ', re.sub('\n', ' ', sql)).strip(), values)

        query = QtSql.QSqlQuery(qApp.connection.database())
        if not query.prepare(sql):
            qApp.loggerDb.error("Query failed '%s'" % queryText)
            if failOnError:
                raise DbError("Failed to perform a query.")
            else:
                writeRecovery(sql, *values)
                self.dbFailed = True
                return

        for value in values:
            query.addBindValue(value)

        if not query.exec_():
            qApp.loggerDb.error("Query failed '%s'" % queryText)
            if failOnError:
                raise DbError(qApp.connection.lastError().text())
            else:
                writeRecovery(sql, *values)
                self.dbFailed = True
                return

        qApp.loggerDb.info("Query passed '%s'" % queryText)

        return query

    def startRun(self):
        sql = "INSERT INTO runs (router) VALUES (?) RETURNING id;"
        query = self.executeQuery(sql, self.id)
        query.first()
        self.currentRun = query.record().value('id')
        qApp.loggerMain.info(
            "Starting a run '%d' for router '%s (%s)'" % (self.currentRun, self.id, self.idHex))

    def createIfNeeded(self):
        sql = "SELECT * FROM routers WHERE id = ?;"
        query = self.executeQuery(sql, self.id)
        if query.size() == 0:
            # Insert record
            sql = "INSERT INTO routers (id) VALUES (?);"
            self.executeQuery(sql, self.id)
            return True
        return False

    def loadSteps(self):
        qApp.loggerMain.info("Loading performed steps.")
        sql = """ SELECT DISTINCT steps.step_name AS name, steps.passed as passed from routers
                  INNER JOIN runs ON runs.router = routers.id
                  INNER JOIN steps ON runs.id = steps.run
                  WHERE routers.id = ?;
              """
        query = self.executeQuery(sql, self.id)
        self.performedSteps = dict(failed=set(), passed=set())
        while query.next():
            if query.record().value('passed'):
                self.performedSteps['passed'].add(query.record().value('name'))
            else:
                self.performedSteps['failed'].add(query.record().value('name'))

        qApp.loggerMain.info("Passed steps: %s" % ", ".join(self.performedSteps['passed']))
        qApp.loggerMain.info("Failed steps: %s" % ", ".join(self.performedSteps['failed']))

    def incStepAttempt(self):
        self.stepAttempt += 1

    def incTestAttempt(self):
        self.testAttempt += 1

    def storeStep(self, name, passed):
        sql = """ INSERT INTO steps (run, step_name, step_order, attempt, passed)
                  VALUES (?, ?, ?, ?, ?);
              """
        order = len(self.performedSteps['passed'])
        self.executeQuery(
            sql, self.currentRun, name, order, self.stepAttempt, passed, failOnError=False)
        if passed:
            self.performedSteps['passed'].add(name)

    def storeTest(self, name, passed):
        sql = """ INSERT INTO tests (run, test_name, attempt, result)
                  VALUES (?, ?, ?, ?);
              """
        self.executeQuery(
            sql, self.currentRun, name, self.testAttempt, passed, failOnError=False)

    def setRunSuccessful(self):
        qApp.loggerMain.info(
            "Run '%d' was successful and router '%s(%s)' is alive" %
            (self.currentRun, self.id, self.idHex)
        )
        sql = "UPDATE runs SET success = true WHERE id = ?;"
        self.executeQuery(sql, self.currentRun, failOnError=False)

    def getTestPlan(self):
        return range(len(tests.TESTS))

    def getStepPlan(self):
        # filter workflow (skipped passed)
        return [
            i for i in range(len(workflow.WORKFLOW))
            if not workflow.WORKFLOW[i].name in self.performedSteps['passed']
        ]

    @property
    def canStartTests(self):
        return self.performedSteps['passed'].issuperset({e.name for e in workflow.WORKFLOW})

    @property
    def canStartSteps(self):
        # at least one step is missing
        return len({e.name for e in workflow.WORKFLOW} - self.performedSteps['passed']) != 0

    def storeFirmware(self, firmware):
        sql = """ INSERT INTO last_seen_firmware (id, firmware)
                  VALUES (?, ?);
              """
        self.executeQuery(sql, self.id, firmware, failOnError=False)
