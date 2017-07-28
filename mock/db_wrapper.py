from application import qApp


def writeRecovery(sql, *values):
    pass


def restoreRecovery():
    qApp.loggerMain.info("Mocking recovery.")


class Router(object):
    _current_run = 0

    @property
    def idHex(self):
        return "%016x" % int(self.id)

    @property
    def currentRun(self):
        return self._current_run

    def __init__(self, routerId):
        self.id = str(routerId).strip()
        self.performedSteps = dict(failed=set(), passed=set())

        self.stepAttempt = 0
        self.testAttempt = 0
        self.dbFailed = False

    def startRun(self, runlist):
        self._current_run += 1
        qApp.loggerMain.info(
            "Starting a mock run %d for router '%s (%s): %s'"
            % (self._current_run, self.id, self.idHex, runlist)
        )
        return self._current_run

    def loadSteps(self):
        qApp.loggerMain.info("Mock - Passed steps: %s" % ", ".join(self.performedSteps['passed']))
        qApp.loggerMain.info("Mock - Failed steps: %s" % ", ".join(self.performedSteps['failed']))

    def incStepAttempt(self):
        self.stepAttempt += 1

    def incTestAttempt(self):
        self.testAttempt += 1

    def storeStep(self, name, passed):
        pass

    def storeTest(self, name, passed):
        pass

    def setRunSuccessful(self):
        qApp.loggerMain.info(
            "Mock Run %d was successful - router '%s(%s)'"
            % (self._current_run, self.id, self.idHex)
        )

    def getTestPlan(self):
        return range(len(qApp.tests.TESTS))

    def getStepPlan(self):
        return range(len(qApp.workflow.WORKFLOW))

    @property
    def canStartTests(self):
        return True

    @property
    def canStartSteps(self):
        return True

    def storeFirmware(self, firmware):
        pass

    def storeRam(self, ram, phase):
        pass

    def storeEeprom(self, eeprom, phase):
        pass

    def storeMcu(self, bootloader, image):
        pass

    def storeUboot(self, image):
        pass

    def storeResult(self, phase, result):
        pass
