#!/usr/bin/env python2
# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.
# licensed under the BSD license

#python modules
import logging
import os
import settings
import subprocess
import sys
from tempfile import mkstemp

# gui related stuff
from PyQt4 import QtGui, QtCore, QtSql
from gui.gui_installer import Ui_Installer

# router object
from router import Router, DbError, DuplicateKey, DoesNotExist
from serial_console import SerialConsole, SCError

# tests
from router_tests import TESTLIST

# settings

#logging
logger = logging.getLogger('installer')
logger.root.setLevel(settings.LOGLEVEL)
nanlogsdir = os.path.join(
    os.path.split(os.path.abspath(__file__))[0], settings.FLASH_LOGS)
logfile = os.path.join(
    os.path.split(os.path.abspath(__file__))[0], settings.LOGFILE)
fh = logging.FileHandler(logfile)
formatter = logging.Formatter(settings.LOGFORMAT)
fh.setFormatter(formatter)
logger.root.addHandler(fh)


USB_RECONNECT_MESSAGE = u"Nezdařila se komunikace se systémem na routru. Zkuste " \
                        u"odpojit a zapojit USB kabel č. 5. Pokud to dále nechcete " \
                        u"zkoušet, zvolte 'Ne'.\nZkusit znovu?"


# code


def serialNumberValidator(sn):
    # serial number must be integer
    try:
        sn = int(sn)
    except ValueError:
        return False

    # it cannot be negative
    if sn < 0:
        return False

    # it must be divisible by 11 or 503316xx (test serie)
    if sn % 11 != 0 and sn / 100 != 503316:
        return False

    return True


def report_tests_results(router):
    "generate test failure list for given router"

    failedTests = [t for t in router.testResults.iterkeys()
                   if router.testResults[t] != router.TEST_OK]
    testsReport = u"<h3>Testy, které selhali</h3>" if failedTests \
                  else u"<h3>Všechny testy proběhli správně</h3>"
    for t in failedTests:
        testsReport += TESTLIST[t]['desc'] + u": "
        if router.testResults[t] == router.TEST_FAIL:
            testsReport += u"neúspěch"
        elif router.testResults[t] == router.TEST_PROBLEM:
            testsReport += u"selhání testu"
        testsReport += u"<br>"

    return testsReport


class FlashingWorker(QtCore.QObject):
    """Flashing Worker which run given commands and returns the status of the
    flashing process.
    """

    # tuple (int code, str msg) code 0 - ok, 1 - router already flashed / error, chceck cables, 2 - final error
    flashFinished = QtCore.pyqtSignal(tuple)
    testFinished = QtCore.pyqtSignal(int, bool, 'QString', 'QString')
    longWaitMsg = QtCore.pyqtSignal(int)

    def __init__(self):
        super(FlashingWorker, self).__init__()
        self.router = None
        self.serialConsole = None
        self.imagesize = os.stat(settings.TFTP_IMAGE_FILE).st_size

    def runCmd(self, cmdWithArgs):
        logger.info("[FLASHWORKER] start flashing (command: `%s`)" % " ".join(cmdWithArgs))
        # TODO self.p - in order to be able to kill the process after some time
        p = subprocess.Popen(cmdWithArgs, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retCode = p.wait()
        stdOut = p.stdout.read().strip()  # TODO handle the case of big outputs in a better way
        return (retCode, stdOut if len(stdOut) < 1001 else (stdOut[:1000] + "... output truncated"))

    @QtCore.pyqtSlot('QString', bool)
    def addNewRouter(self, routerId, nextAttempt):
        if self.serialConsole:
            try:
                self.serialConsole.close()
            except Exception:
                pass

        routerId = str(routerId)

        dbErr = False
        try:
            if nextAttempt:
                self.router = Router.nextAttempt(str(routerId))  # add next attempt to flash
            else:
                self.router = Router.createNewRouter(str(routerId))  # try to create new router
            return_code = self.router.status
            err_msg = ""
        except DuplicateKey:
            return_code = -1
            err_msg = u"O tomhle routeru je v databázi záznam, že už byl naflashován, " \
                      u"přejete si to zkusit znovu?"
        except DoesNotExist:
            logger.critical("[FLASHWORKER] adding new flash attempt to db failed, "
                            "no router with this id (routerId=%s). This should never "
                            "happen. It is a bug in this application."
                            % routerId)
            return_code = -2
            err_msg = u"Vyskytla se chyba, která by se nikdy neměla. Prosím, restartujte program."
        except DbError, e:
            return_code = -2
            err_msg = e.message
            dbErr = True

        self.flashFinished.emit((return_code, err_msg, dbErr))

    @QtCore.pyqtSlot('QString')
    def getFlashedRouter(self, routerId):
        if self.serialConsole:
            try:
                self.serialConsole.close()
            except Exception:
                pass

        routerId = str(routerId)

        dbErr = False
        try:
            self.router = Router.fetchFromDb(routerId)  # get last attempt for given id router
            return_code = self.router.status
            err_msg = ""
        except DoesNotExist:
            return_code = -1
            err_msg = u"Router s daným ID ještě nebyl naprogramován, musíte ho nejdříve " \
                      u"naprogramovat, až pak testovat."
        except DbError, e:
            return_code = -2
            err_msg = e.message
            dbErr = True

        self.flashFinished.emit((return_code, err_msg, dbErr))

    @QtCore.pyqtSlot()
    def flashStepI2C(self):
        logger.debug("[FLASHWORKER] starting first step (routerId=%s)" % self.router.id)
        p_return = self.runCmd((settings.STEP_I2C_CMD, self.router.id))

        return_code = 0
        err_msg = ""

        if p_return[0] == 0:
            logger.info("[FLASHWORKER] I2C step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_I2C
            self.router.error = ""
        elif self.router.secondChance['I2C'] and not p_return[1].split("\n", 1)[0].endswith("OK"):
            # if a user has a second chance (will check the cables,...) and first thing hasn't
            # passed (is not 'something... OK')
            logger.warning("[FLASHWORKER] I2C step failed, check the cables (routerId=%s)" % self.router.id)
            self.router.secondChance['I2C'] = False
            self.router.error = p_return[1]
            return_code = 1
            err_msg = u"Programování zařízení na I2C sběrnici selhalo. Prosím ověřte zapojení kabelu 1 " \
                      u"(Zapojen z TURRIS PROGRAMMERu konektor P1 na programovaný TURRIS konektor J2). " \
                      u" Zkontrolujte připojení napájecího adaptéru 7,5V."
        else:
            logger.warning("[FLASHWORKER] I2C step failed definitely (routerId=%s)" % self.router.id)
            self.router.error = p_return[1]
            return_code = 2
            err_msg = u"Flashování I2C selhalo."

        dbErr = not self.router.save()

        self.flashFinished.emit((return_code, err_msg, dbErr))

    @QtCore.pyqtSlot()
    def flashStepCPLD(self):
        logger.debug("[FLASHWORKER] starting second step (routerId=%s)" % self.router.id)
        # create a log file
        tmpf_fd, tmpf_path = mkstemp(text=True)

        # execute the command
        p_return = self.runCmd((settings.STEP_CPLD_CMD, "-infile", settings.CPLD_FLASH_INFILE, "-logfile", tmpf_path))

        # read the log file
        log_content = ""
        tmpr = os.read(tmpf_fd, 1024)
        while tmpr:
            log_content += tmpr
            tmpr = os.read(tmpf_fd, 1024)
        log_content = log_content.strip()

        return_code = 0
        err_msg = ""
        if log_content.endswith("Operation: successful."):
            logger.info("[FLASHWORKER] CPLD step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_CPLD
            self.router.error = ""
        elif self.router.secondChance['CPLD']:
            logger.warning("[FLASHWORKER] CPLD step failed, check the cables (routerId=%s)" % self.router.id)
            self.router.secondChance['CPLD'] = False
            self.router.error = log_content
            return_code = 1
            err_msg = u"Programování CPLD obvodu selhalo. Prosím ověřte zapojení kabelu 2 " \
                      u"(Zapojen z USB portu PC na programovaný TURRIS konektor J7). " \
                      u"Zkontrolujte připojení napájecího adaptéru 7,5V."
        else:
            logger.warning("[FLASHWORKER] CPLD step failed definitely (routerId=%s)" % self.router.id)
            self.router.error = log_content
            return_code = 2
            err_msg = u"Flashování CPLD selhalo."

        # close and delete the log file
        os.close(tmpf_fd)
        os.remove(tmpf_path)

        dbErr = not self.router.save()

        self.flashFinished.emit((return_code, err_msg, dbErr))

    @QtCore.pyqtSlot()
    def flashStepFlashing(self):
        logger.debug("[FLASHWORKER] starting third step (routerId=%s)" % self.router.id)

        retStr, retryError = self.go_to_flash()
        if retStr:
            # error
            if retryError:
                return_code = 3  # special case, show dialog box
            else:
                return_code = 1 if self.router.secondChance["NOR"] else 2
                self.router.secondChance["NOR"] = False
            err_msg = retStr
            self.router.error = "error when flashing NOR using uboot"
            dbErr = not self.router.save()
            logger.info("[FLASHWORKER] FLASH step failed (routerId=%s)" % self.router.id)
        else:
            # everything ok
            return_code = 0
            err_msg = ""
            dbErr = False

            logger.info("[FLASHWORKER] FLASH step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_FLASHED
            self.router.error = ""
            dbErr = not self.router.save()

        # if final error, close the console
        if return_code == 2 and self.serialConsole:
            self.serialConsole.close()
            self.serialConsole = None

        self.flashFinished.emit((return_code, err_msg, dbErr))

    def go_to_factory_reset(self):
        logger.debug("[FLASHWORKER] starting to perform factory reset (routerId=%s)"
                     % self.router.id)

        # create and prepare a serial console connection
        if self.serialConsole is None:
            # find ttyUSBx
            dev = [t for t in os.listdir("/dev/") if t.startswith("ttyUSB")]
            if len(dev) != 1:
                if len(dev) == 0:
                    return (u"Zkontrolujte kabel č. 5, nenašel jsem sériovou konzoli.", False)
                else:
                    return (u"Našel jsem více sériových konzolí, nevím kterou použít.", False)

            # open the console
            try:
                self.serialConsole = SerialConsole("/dev/" + dev[0])
            except Exception, e:
                return (u"Nezdařilo se otevřít spojení přes konzoli.", False)

        try:
            # to_factory_reset(timeout=-1) - wait forever
            # (there is a button to interrupt the wait)
            self.serialConsole.to_system()
        except SCError, e:
            logger.warning("[FLASHWORKER] Serial console initialization failed (routerId=%s). "
                           % self.router.id + str(e) + "\n" + self.serialConsole.inbuf)
            self.serialConsole.close()
            self.serialConsole = None
            return (u"Nezdařil se Factory reset.", True)
        except Exception, e:  # serial console exception, IOError,...
            logger.warning("[FLASHWORKER] Serial console initialization failed (Exception other than SCError) (routerId=%s). "
                           % self.router.id + str(e))
            self.serialConsole.close()
            self.serialConsole = None
            return (u"Nezdařil se Factory reset.", False)

        # we are in uboot, move to the next window (with statusbar)
        return ("", False)

    def go_to_flash(self):
        logger.debug("[FLASHWORKER] starting to FLASH (routerId=%s)" % self.router.id)

        # create and prepare a serial console connection
        if self.serialConsole is None:
            # find ttyUSBx
            dev = [t for t in os.listdir("/dev/") if t.startswith("ttyUSB")]
            if len(dev) != 1:
                if len(dev) == 0:
                    return (u"Zkontrolujte kabel č. 5, nenašel jsem sériovou konzoli.", False)
                else:
                    return (u"Našel jsem více sériových konzolí, nevím kterou použít.", False)

            # open the console
            try:
                self.serialConsole = SerialConsole("/dev/" + dev[0])
            except Exception, e:
                return (u"Nezdařilo se otevřít spojení přes konzoli.", False)

        try:
            # to_flash(timeout=-1) - wait forever
            # (there is a button to interrupt the wait)
            self.serialConsole.to_flash(-1)
        except SCError, e:
            logger.warning("[FLASHWORKER] Serial console initialization failed (routerId=%s). "
                           % self.router.id + str(e) + "\n" + self.serialConsole.inbuf)
            self.serialConsole.close()
            self.serialConsole = None
            return (u"Nezdařilo se dostat naflashovat NOR.", True)
        except Exception, e:  # serial console exception, IOError,...
            logger.warning("[FLASHWORKER] Serial console initialization failed (Exception other than SCError) (routerId=%s). "
                           % self.router.id + str(e))
            self.serialConsole.close()
            self.serialConsole = None
            return (u"Nezdařilo se dostat naflashovat NOR.", False)

        return ("", False)

    @QtCore.pyqtSlot()
    def doFactoryReset(self):
        logger.debug("[FLASHWORKER] starting FACTORY RESET (routerId=%s)"
                     % self.router.id)

        retStr, retryError = self.go_to_factory_reset()
        if retStr:
            # error
            if retryError:
                return_code = 3  # special case, show dialog box
            else:
                return_code = 1 if self.router.secondChance["NOR"] else 2
                self.router.secondChance["NOR"] = False
            err_msg = retStr
            self.router.error = "error when performing factory reset"
            dbErr = not self.router.save()
            logger.info("[FLASHWORKER] FACTORY RESET step failed (routerId=%s)"
                        % self.router.id)
        else:
            # everything ok
            return_code = 0
            err_msg = ""
            dbErr = False

            logger.info("[FLASHWORKER] FACTORY RESET step successful (routerId=%s)"
                        % self.router.id)
            self.router.status = self.router.STATUS_FINISHED
            self.router.error = ""
            dbErr = not self.router.save()

        # if final error, close the console
        if return_code == 2 and self.serialConsole:
            self.serialConsole.close()
            self.serialConsole = None

        self.flashFinished.emit((return_code, err_msg, dbErr))

    def testPrepareConsole(self):
        logger.debug("[TESTING] Executing test %d on the router with routerId=%s" %
                     (self.router.currentTest, self.router.id))

        # create and prepare a serial console connection
        if self.serialConsole is None:
            # find ttyUSBx
            dev = [t for t in os.listdir("/dev/") if t.startswith("ttyUSB")]
            if len(dev) != 1:
                if len(dev) == 0:
                    errMsg = u"Zkontrolujte kabel č. 5, nenašel jsem sériovou konzoli."
                else:
                    errMsg = u"Našel jsem více sériových konzolí, nevím kterou použít."
                return (errMsg, False)
            # open the console
            try:
                self.serialConsole = SerialConsole("/dev/" + dev[0])
            except Exception, e:
                return (u"Nezdařilo se otevřít spojení přes konzoli. Zkontrolujte, "
                        u"kabel č. 5 a napájení 7,5V.", False)
            self.serialConsole.state = self.serialConsole.UNDEFINED

        if self.serialConsole.state != self.serialConsole.OPENWRT:
            try:
                self.serialConsole.to_system()
            except SCError, e:
                logger.warning("[TESTING] Serial console initialization failed (routerId=%s). "
                               % self.router.id + str(e) + "\n" + self.serialConsole.inbuf)
                if not self.serialConsole.inbuf:
                    # no output from serial console, deconnect and reconnect the usb cable
                    return_status = (USB_RECONNECT_MESSAGE, True)
                else:
                    return_status = (u"Nezdařila se komunikace se systémem na routru.", False)
                self.serialConsole.close()
                self.serialConsole = None
                return return_status
            except Exception, e:  # serial console exception, IOError,...
                logger.warning("[TESTING] Serial console initialization failed (Exception other than SCError) (routerId=%s). "
                               % self.router.id + str(e))
                self.serialConsole.close()
                self.serialConsole = None
                # self.router.testResults[self.router.currentTest] = self.router.TEST_PROBLEM
                return (u"Při komunikaci s routrem přes sériovou "
                        u"konzoli došlo k chybě.", False)

    @QtCore.pyqtSlot()
    def executeTest(self):
        # prepare the serial console
        cons_prep_err = self.testPrepareConsole()
        if cons_prep_err:
            self.router.testResults[self.router.currentTest] = self.router.TEST_PROBLEM
            if cons_prep_err[1]:
                self.testFinished.emit(self.router.currentTest, True,
                                       cons_prep_err[0], u"Problém sériové konzole.")
            elif self.router.testSecondChance:
                self.router.testSecondChance = False
                self.testFinished.emit(self.router.currentTest, False,
                                       cons_prep_err[0], u"Problém sériové konzole.")
            else:
                self.testFinished.emit(-1, False, cons_prep_err[0],
                                       report_tests_results(self.router))
            return

        # run the test
        errMsg = ""
        testResult = ""
        try:
            p_return = TESTLIST[self.router.currentTest]['testfunc'](self.serialConsole)
        except Exception:
            self.router.testResults[self.router.currentTest] = self.router.TEST_PROBLEM
            errMsg = u"Vyskytla se chyba při testování, sériová konzole " \
                     u"vrátila výsledek, který nedokážu zpracovat."
            testResult = TESTLIST[self.router.currentTest]['desc'] + \
                u" skončil s chybou:<br>Chyba konzole."
            if self.router.testSecondChance:
                self.router.testSecondChance = False
                nextTest = self.router.currentTest
            else:
                nextTest = -1
            import traceback
            logger.critical("[TESTING] error during test \"" +
                            TESTLIST[self.router.currentTest]['desc'] +
                            "\"\n" +
                            traceback.format_exc() +
                            "\n" + self.serialConsole.inbuf)
            self.serialConsole.close()
            self.serialConsole = None
        else:
            if p_return[0] == 0:
                self.router.testResults[self.router.currentTest] = self.router.TEST_OK
                testResult = TESTLIST[self.router.currentTest]['desc'] + u" proběhl úspěšně"
            else:
                testResult = u"%s skončil s chybou:<div style=\"font-size: 11px;\">%s</div>" % (
                    TESTLIST[self.router.currentTest]['desc'].capitalize(),
                    TESTLIST[self.router.currentTest]['interpretfailure'](p_return)
                )
                self.router.testResults[self.router.currentTest] = self.router.TEST_FAIL

            # save to db the test result p_return[0]
            self.router.saveTestResult(
                p_return[0],
                ""
                if p_return[0] == 0 else
                p_return[1] + "\n-----\n" + p_return[2] + "\n-----\n" + p_return[3]
            )

            self.router.currentTest += 1
            if self.router.currentTest >= len(TESTLIST):
                try:
                    # delete /etc/config/wireless because it contains 2 radios
                    # it will be regenerated the very next boot
                    self.serialConsole.exec_("rm /etc/config/wireless")
                except:
                    pass
                try:
                    self.serialConsole.close()
                    self.serialConsole = None
                except:
                    pass
                nextTest = -1
            else:
                nextTest = self.router.currentTest

        if nextTest == -1:
            testResult += report_tests_results(self.router)

        self.testFinished.emit(nextTest, False, errMsg, testResult)

    @QtCore.pyqtSlot()
    def stepCpldEraser(self):
        logger.debug("[FLASHWORKER] starting cpld erasing step (routerId=%s)" % "not specified")  # self.router.id)
        # create a log file
        tmpf_fd, tmpf_path = mkstemp(text=True)

        # execute the command
        p_return = self.runCmd((settings.STEP_CPLD_CMD, "-infile", settings.CPLD_ERASE_INFILE, "-logfile", tmpf_path))

        # read the log file
        log_content = ""
        tmpr = os.read(tmpf_fd, 1024)
        while tmpr:
            log_content += tmpr
            tmpr = os.read(tmpf_fd, 1024)
        log_content = log_content.strip()

        if log_content.endswith("Operation: successful."):
            logger.info("[FLASHWORKER] CPLD erase successful (routerId=%s)"
                        % "not specified")  # self.router.id)
            # set self.router.status and error to something reasonable
            # self.router.error = ""
            return_code = 0
            err_msg = ""
        else:
            logger.warning("[FLASHWORKER] CPLD erasing failed, check the cables (routerId=%s)"
                           % "not specified")  # self.router.id)
            # self.router.error = log_content
            return_code = 1
            err_msg = u"Mazání CPLD obvodu selhalo. Prosím ověřte zapojení kabelu 2 " \
                      u"(Zapojen z USB portu PC na programovaný TURRIS konektor J7). " \
                      u"Zkontrolujte připojení napájecího adaptéru 7,5V."

        # close and delete the log file
        os.close(tmpf_fd)
        os.remove(tmpf_path)

        # dbErr = not self.router.save()
        dbErr = False

        self.flashFinished.emit((return_code, err_msg, dbErr))


class Installer(QtGui.QMainWindow, Ui_Installer):
    """Installer GUI application for flashing the Turris routers"""

    newRouterAddSig = QtCore.pyqtSignal('QString', bool)
    flashStepI2CSig = QtCore.pyqtSignal()
    flashStepCPLDSig = QtCore.pyqtSignal()
    flashStepFlashingSig = QtCore.pyqtSignal()
    runTestSig = QtCore.pyqtSignal()
    checkRouterDbExistsSig = QtCore.pyqtSignal('QString')
    cpldStartEraseSig = QtCore.pyqtSignal()
    factoryResetSig = QtCore.pyqtSignal()

    STEPS = {
        'START': 0,
        'SCAN': 1,
        'I2C': 2,
        'CPLD': 3,
        'FLASH': 4,
        'FACTORYRESET': 5,
        'BEFORETESTS': 6,
        'CHCKCABLE': 7,
        'ERROR': 8,
        'TESTPREPARE': 9,
        'TESTEXEC': 10,
        'FINISH': 11,
        'ACCESSORIES': 12,
        'ACCTESTS': 13,
        'ACCCPLDERASE': 14
    }

    STEP_NUM_TO_ID = {v: k for k, v in STEPS.iteritems()}

    # working modes
    FLASHING = 0
    TESTING = 1

    def __init__(self):
        super(Installer, self).__init__()

        self.setupUi(self)  # create gui
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.blockClose = False
        self.working_mode = self.FLASHING

        # buttons event listeners
        self.startToScan.clicked.connect(self.simpleMoveToScan)
        self.scanToProgramming.clicked.connect(self.launchProgramming)
        self.flashingTimeoutButton.clicked.connect(self.interruptWait)
        self.factoryResetTimeoutButton.clicked.connect(self.interruptWait)
        self.prepareToFirstTest.clicked.connect(self.toNextTest)
        self.chckToStepX.clicked.connect(self.userHasCheckedCables)
        self.errToScan.clicked.connect(self.simpleMoveToScan)
        self.prepTestToRunTest.clicked.connect(self.startPreparedTest)
        self.endToScan.clicked.connect(self.toNextRouter)
        self.toAccessoriesTests.clicked.connect(self.showOnlyTests)
        self.toAccessoriesCPLDErase.clicked.connect(self.showCpldEraser)
        self.toOnlyTests.clicked.connect(self.chckRouterAndTest)
        self.startEraseCpld.clicked.connect(self.eraseCpld)

        # action trigger slots
        self.actionKonec.triggered.connect(self.close)
        self.actionUvodniObrazovka.triggered.connect(self.simpleMoveToScan)
        self.actionDalsifunkce.triggered.connect(self.showAccessories)
        self.actionTestovani.triggered.connect(self.showOnlyTests)
        self.actionSmazaniCPLD.triggered.connect(self.showCpldEraser)

        # start a second thread which will do the flashing
        self.flashWorker = FlashingWorker()
        self.flashThread = QtCore.QThread()

        self.newRouterAddSig.connect(self.flashWorker.addNewRouter)
        self.flashStepI2CSig.connect(self.flashWorker.flashStepI2C)
        self.flashStepCPLDSig.connect(self.flashWorker.flashStepCPLD)
        self.flashStepFlashingSig.connect(self.flashWorker.flashStepFlashing)
        self.runTestSig.connect(self.flashWorker.executeTest)
        self.checkRouterDbExistsSig.connect(self.flashWorker.getFlashedRouter)
        self.flashWorker.flashFinished.connect(self.moveToNext)
        self.flashWorker.testFinished.connect(self.toNextTest)
        self.flashWorker.longWaitMsg.connect(self.informLongWait)
        self.cpldStartEraseSig.connect(self.flashWorker.stepCpldEraser)
        self.factoryResetSig.connect(self.flashWorker.doFactoryReset)

        self.flashWorker.moveToThread(self.flashThread)
        self.flashThread.start()

        # create a database connection, but do not open it, until necessary
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(settings.DB_HOST)
        self.db.setUserName(settings.DB_USER)
        self.db.setPassword(settings.DB_PASS)
        self.db.setDatabaseName(settings.DB_DBNAME)

        self.flashingStage = 0  # we start at zero, (start page)

        # try to create nanlogsdir if doesn't exist
        try:
            if not os.path.exists(nanlogsdir):
                os.mkdir(nanlogsdir)
        except (IOError, OSError):
            logger.critical("[MAIN] could not create directory "
                            "for saving session.log (%s)" % nanlogsdir)

    @QtCore.pyqtSlot()
    def simpleMoveToScan(self):
        """switch to the Scan page when clicked on a button"""
        self.working_mode = self.FLASHING
        self.lineEdit.clear()
        self.lineEdit.setFocus()
        self.scanToProgramming.setEnabled(True)
        self.stackedWidget.setCurrentIndex(self.STEPS['SCAN'])

    @QtCore.pyqtSlot()
    def toNextRouter(self):
        if self.working_mode == self.FLASHING:
            self.simpleMoveToScan()
        else:  # self.working_mode == self.TESTING
            self.showOnlyTests()

    @QtCore.pyqtSlot()
    def launchProgramming(self):
        """do the check of scanned id, take it, add to db, and start flashing"""
        barCode = self.lineEdit.text()
        if barCode.isEmpty():
            QtGui.QMessageBox.warning(
                self, u"Chyba", u"Musíte naskenovat čárový kód.")
            self.simpleMoveToScan()
            return

        if not serialNumberValidator(barCode):
            QtGui.QMessageBox.warning(
                self, u"Chyba", u"Neplatný čárový kód, naskenujte ho znovu.")
            self.simpleMoveToScan()
            return

        # two possibilities, this id is/is not in the db
        self.scanToProgramming.setEnabled(False)
        self.blockClose = True
        self.newRouterAddSig.emit(barCode, False)

    @QtCore.pyqtSlot(tuple)
    def moveToNext(self, flash_result = None):
        """slot for signals from flashWorker in flashThread"""

        i = self.stackedWidget.currentIndex()

        if i == self.STEPS['SCAN']:
            if flash_result[0] >= 0:
                # start with step given in flash_result[0]
                if flash_result[0] == 0:
                    i = self.STEPS['I2C']
                    self.flashStepI2CSig.emit()
                elif flash_result[0] == 1:
                    i = self.STEPS['CPLD']
                    self.flashStepCPLDSig.emit()
                elif flash_result[0] == 2:
                    i = self.STEPS['FLASH']
                    self.flashStepFlashingSig.emit()
                elif flash_result[0] == 3:
                    self.factoryResetSig.emit()
                    i = self.STEPS['FACTORYRESET']
                elif flash_result[0] == 4:
                    i = self.STEPS['BEFORETESTS']
                self.flashingStage = i
            elif flash_result[0] == -1:
                # router already exists
                if QtGui.QMessageBox.question(
                    self, 'Router existuje', flash_result[1],
                    buttons=QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                    defaultButton=QtGui.QMessageBox.Cancel
                ) == QtGui.QMessageBox.Ok:
                    # start another attempt to flash the router
                    barCode = self.lineEdit.text()
                    self.newRouterAddSig.emit(barCode, True)
                else:
                    # continue with other router
                    self.blockClose = False
                    self.scanToProgramming.setEnabled(True)
                    self.lineEdit.clear()
                    self.lineEdit.setFocus()
                return
            else:
                # db error, flash_result[0] == -2
                self.blockClose = False
                self.scanToProgramming.setEnabled(True)
                QtGui.QMessageBox.warning(self, u"Chyba", flash_result[1])
                self.lineEdit.setFocus()
                return
        elif i == self.STEPS['I2C']:
            if flash_result[0] == 0:
                i = self.STEPS['CPLD']
                self.flashingStage = i
                self.flashStepCPLDSig.emit()
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['CPLD']:
            if flash_result[0] == 0:
                i = self.STEPS['FLASH']
                self.flashingStage = i
                self.flashStepFlashingSig.emit()
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['FLASH']:
            if flash_result[0] == 0:
                i = self.STEPS['FACTORYRESET']
                self.flashingStage = i
                self.factoryResetSig.emit()  # wait for RESET button pressed
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['FACTORYRESET']:
            if flash_result[0] == 0:
                i = self.STEPS['BEFORETESTS']
                self.flashingStage = 0
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['ACCTESTS']:
            self.toOnlyTests.setEnabled(True)
            if flash_result[2]:
                QtGui.QMessageBox.warning(self, u"Chyba databáze", flash_result[1])
            elif flash_result[0] == -1:
                QtGui.QMessageBox.warning(self, u"Chyba", flash_result[1])
                self.barcodeOnlyTests.clear()
                self.barcodeOnlyTests.setFocus()
            else:
                self.toNextTest()
            return
        elif i == self.STEPS['ACCCPLDERASE']:
            if flash_result[0] < 0:
                QtGui.QMessageBox.warning(self, u"Chyba", flash_result[1])
                self.cpldDeleteStack.setCurrentIndex(0)
            else:
                QtGui.QMessageBox.warning(self, u"Smazáno", u"CPLD obvod byl úspěšně smazán.")
                self.stackedWidget.setCurrentIndex(self.STEPS['START'])
            return

        if i in (self.STEPS['BEFORETESTS'], self.STEPS['ERROR']):
            # unblock the possibility to close the app
            self.blockClose = False

        # change the stackedWidget index
        self.stackedWidget.setCurrentIndex(i)
        logger.debug("[MAIN] switching to the step %d(%s)"
                     % (i, Installer.STEP_NUM_TO_ID.get(i, "")))

    @QtCore.pyqtSlot(int)
    def informLongWait(self, step):
        PROGRESS_STEPS = [1, 4, 5, 25, 45, 85]
        self.progressBar_6.setValue(PROGRESS_STEPS[step])

    @QtCore.pyqtSlot()
    def userHasCheckedCables(self):
        # change the stackedWidget to self.flashingStage and emmit the corresponding signal
        self.stackedWidget.setCurrentIndex(self.flashingStage)
        if self.flashingStage == self.STEPS['I2C']:
            self.flashStepI2CSig.emit()
        elif self.flashingStage == self.STEPS['CPLD']:
            self.flashStepCPLDSig.emit()
        elif self.flashingStage == self.STEPS['FLASH']:
            self.flashStepFlashingSig.emit()
        elif self.flashingStage == self.STEPS['FACTORYRESET']:
            self.factoryResetSig.emit()

    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int, bool, 'QString', 'QString')
    def toNextTest(self, testNum=0, questionContinue=False, errorText="", testResult=""):
        """current test finished, show given test instructions or "theEnd"
        page if testNum = -1"""
        if questionContinue:
            if QtGui.QMessageBox.question(
                self, u"Chyba", errorText,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            ) != QtGui.QMessageBox.Yes:
                testNum = -1
                testResult = u"Výsledek předchozího testu:<br>%s" % testResult + \
                             report_tests_results(self.flashWorker.router)
        elif errorText:
            QtGui.QMessageBox.warning(self, u"Chyba", errorText)

        if testNum == -1:
            # no more tests
            self.finalSummary.setText(testResult)
            nextPage = self.STEPS['FINISH']
        else:
            nextPage = self.STEPS['TESTPREPARE']
            if testResult:
                testResult = u"Výsledek předchozího testu:<br>%s" \
                    % testResult.replace("\n", "<br>\n")
            self.testResultLabel.setText(testResult)
            self.nextTestDesc.setText(u"Následující test je %s." % TESTLIST[testNum]['desc']
                                      + u"\n" + TESTLIST[testNum]['instructions'])

        self.stackedWidget.setCurrentIndex(nextPage)

    @QtCore.pyqtSlot()
    def startPreparedTest(self):
        self.runTestSig.emit()
        self.runningTestDesc.setText(u"Probíhající test je " + self.nextTestDesc.text()[20:].split("\n", 1)[0])
        self.stackedWidget.setCurrentIndex(self.STEPS['TESTEXEC'])

    @QtCore.pyqtSlot()
    def routerReset(self):
        self.flashingStage = self.STEPS['FLASH']
        self.flashStepFlashingSig.emit()
        self.stackedWidget.setCurrentIndex(self.flashingStage)

    @QtCore.pyqtSlot()
    def simpleNextPage(self):
        i = self.stackedWidget.currentIndex()
        i += 1
        self.flashingStage = i
        self.stackedWidget.setCurrentIndex(i)

    @QtCore.pyqtSlot()
    def showAccessories(self):
        self.stackedWidget.setCurrentIndex(self.STEPS['ACCESSORIES'])

    @QtCore.pyqtSlot()
    def showOnlyTests(self):
        self.working_mode = self.TESTING
        self.barcodeOnlyTests.clear()
        self.stackedWidget.setCurrentIndex(self.STEPS['ACCTESTS'])
        self.barcodeOnlyTests.setFocus()

    @QtCore.pyqtSlot()
    def showCpldEraser(self):
        self.cpldDeleteStack.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(self.STEPS['ACCCPLDERASE'])

    @QtCore.pyqtSlot()
    def eraseCpld(self):
        self.cpldDeleteStack.setCurrentIndex(1)
        self.cpldStartEraseSig.emit()

    @QtCore.pyqtSlot()
    def chckRouterAndTest(self):
        """do the check of scanned id, check if that router exists in db"""
        barCode = self.barcodeOnlyTests.text()
        if barCode.isEmpty():
            QtGui.QMessageBox.critical(
                self, u"Chyba", u"Musíte naskenovat čárový kód.")
            self.barcodeOnlyTests.clear()
            self.barcodeOnlyTests.setFocus()
            return

        if not serialNumberValidator(barCode):
            QtGui.QMessageBox.critical(
                self, u"Chyba", u"Neplatný čárový kód, naskenujte ho znovu.")
            self.barcodeOnlyTests.clear()
            self.barcodeOnlyTests.setFocus()
            return

        # check if this router is in db and set router id and attempt accordingly
        self.toOnlyTests.setEnabled(False)
        self.checkRouterDbExistsSig.emit(barCode)

    @QtCore.pyqtSlot()
    def interruptWait(self):
        try:
            self.flashWorker.serialConsole.interrupt_wait()
        except:
            pass

    def closeEvent(self, event):
        if self.blockClose:
            if QtGui.QMessageBox.question(
                self, u"Pracuju",
                u"Probíhá flashování, skutečně chcete program zavřít? "
                u"Router se může špatně naprogramovat. Hlavně první krok "
                u"(I2C) je kritický.",
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
            ) != QtGui.QMessageBox.Ok:
                event.ignore()
                return
            else:
                logger.critical("[MAIN] closing the application while flashWorker still running")

        # close the database
        if self.db.isOpen():
            self.db.close()
        self.flashThread.quit()
        event.accept()


def main():
    logger.info("[MAIN] starting the application")

    app = QtGui.QApplication(sys.argv)
    widget = Installer()
    widget.show()
    ret_status = app.exec_()

    logger.info("[MAIN] closing the application with status %d" % ret_status)
    sys.exit(ret_status)

if __name__ == '__main__':
    main()
