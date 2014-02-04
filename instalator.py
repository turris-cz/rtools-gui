#!/usr/bin/env python2
# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.
# licensed under the BSD license

#python modules
import logging
import os
import subprocess
import sys
from shutil import copy
from tempfile import mkstemp
from time import sleep

# gui related stuff
from PyQt4 import QtGui, QtCore, QtSql
from gui import uiresources
from gui.gui_installer import Ui_Installer

# router object
from router import Router, DbError, DuplicateKey, DoesNotExist
from serial_console import SerialConsole, SCError

# tests
from router_tests import TESTLIST

# settings
from settings import *

#logging
logger = logging.getLogger('installer')
logger.root.setLevel(LOGLEVEL)
nanlogsdir = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                   FLASH_LOGS)
logfile = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                   LOGFILE)
fh = logging.FileHandler(logfile)
formatter = logging.Formatter(LOGFORMAT)
fh.setFormatter(formatter)
logger.root.addHandler(fh)


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


class FlashingWorker(QtCore.QObject):
    """Flashing Worker which run given commands and returns the status of the
    flashing process.
    """
    
    # tuple (int code, str msg) code 0 - ok, 1 - router already flashed / error, chceck cables, 2 - final error
    flashFinished = QtCore.pyqtSignal(tuple)
    testFinished = QtCore.pyqtSignal(int, 'QString', 'QString')
    
    def __init__(self):
        super(FlashingWorker, self).__init__()
        self.router = None
        self.serialConsole = None
        self.imagesize = os.stat(TFTP_IMAGE_FILE).st_size
    
    def runCmd(self, cmdWithArgs):
        logger.info("[FLASHWORKER] start flashing (command: `%s`)" % " ".join(cmdWithArgs))
        # TODO self.p - in order to be able to kill the process after some time
        p = subprocess.Popen(cmdWithArgs, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retCode = p.wait()
        stdOut = p.stdout.read().strip() # TODO handle the case of big outputs in a better way
        return (retCode, stdOut if len(stdOut) < 1001 else (stdOut[:1000] + "... output truncated"))
    
    @QtCore.pyqtSlot('QString', bool)
    def addNewRouter(self, routerId, nextAttempt):
        routerId = str(routerId)
        
        dbErr = False
        try:
            if nextAttempt:
                self.router = Router.nextAttempt(str(routerId)) # add next attempt to flash
            else:
                self.router = Router.createNewRouter(str(routerId)) # try to create new router
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
        routerId = str(routerId)
        
        dbErr = False
        try:
            self.router = Router.fetchFromDb(routerId) # get last attempt for given id router
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
    def flashStepOne(self):
        logger.debug("[FLASHWORKER] starting first step (routerId=%s)" % self.router.id)
        p_return = self.runCmd((STEP_I2C_CMD, self.router.id))
        
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
    def flashStepTwo(self):
        logger.debug("[FLASHWORKER] starting second step (routerId=%s)" % self.router.id)
        # create a log file
        tmpf_fd, tmpf_path = mkstemp(text=True)
        
        # execute the command
        p_return = self.runCmd((STEP_CPLD_CMD, "-infile", CPLD_FLASH_INFILE, "-logfile", tmpf_path))
        
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
    def flashStepThree(self):
        logger.debug("[FLASHWORKER] starting third step (routerId=%s)" % self.router.id)
        p_return = self.runCmd(("/bin/bash", STEP_FLASH_CMD))
        
        # copy and send log_backup
        persistentLog = os.path.join(nanlogsdir, "%s-%d-%s.log" %
                (self.router.id, self.router.attempt,
                 self.router.secondChance['FLASH'] and "0" or "1"))
        try:
            copy(STEP_FLASH_LOGFILE, persistentLog)
            self.runCmd((LOG_BACKUP_CMD, persistentLog))
        except Exception: # IOError, OSError, ...?
            pass
        
        return_code = 0
        err_msg = ""
        
        try:
            with open(STEP_FLASH_LOGFILE, "r") as fh:
                logtext = fh.read()
        except IOError:
            logger.critical("[FLASHWORKER] Could not read codewarrior session.log, application error")
            logtext = "Error"
            # FIXME maybe close the application now
        
        cableDisconnected = logtext.find("Cable disconnected") >= 0
        if cableDisconnected and self.router.secondChance['FLASH']:
            # cable disconnected,
            logger.warning("[FLASHWORKER] FLASH step failed, check the cables (routerId=%s)" % self.router.id)
            self.router.secondChance['FLASH'] = False
            self.router.error = "Flashing exited with \"Cable disconnected\" in session.log\n"
            return_code = 1
            err_msg = u"Programování NOR Flash selhalo. Prosím ověřte zapojení kabelu 3 " \
                      u"(Zapojen z USB portu PC na programovaný TURRIS konektor P2). " \
                      u"Zkontrolujte připojení napájecího adaptéru 7,5V."
        elif logtext.find("Error") >= 0 or (cableDisconnected and not self.router.secondChance['FLASH']):
            logger.warning("[FLASHWORKER] FLASH step failed definitely (routerId=%s)" % self.router.id)
            self.router.error = "Flashing exited with \"Error\" in session.log"
            return_code = 2
            err_msg = u"Flashování NAND a NOR selhalo."
        else:
            # TODO is there a Diagnose Succeeded string?
            logger.info("[FLASHWORKER] FLASH step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_UBOOT
            self.router.error = ""
        
        dbErr = not self.router.save()
        
        self.flashFinished.emit((return_code, err_msg, dbErr))
    
    
    def go_to_uboot(self):
        logger.debug("[FLASHWORKER] starting fourth step (routerId=%s)" % self.router.id)
        
        # create and prepare a serial console connection
        if self.serialConsole is None:
            # find ttyUSBx
            dev = [t for t in os.listdir("/dev/") if t.startswith("ttyUSB")]
            if len(dev) != 1:
                if len(dev) == 0:
                    return u"Zkontrolujte kabel č. 5, nenašel jsem sériovou konzoli."
                else:
                    return u"Našel jsem více sériových konzolí, nevím kterou použít."
            
            # open the console
            try:
                self.serialConsole = SerialConsole("/dev/" + dev[0])
            except Exception, e:
                return u"Nezdařilo se otevřít spojení přes konzoli."
        
        try:
            self.serialConsole.to_uboot()
        except SCError, e:
            logger.warning("[FLASHWORKER] Serial console initialization failed (routerId=%s). "
                            % self.router.id + str(e))
            self.serialConsole.close()
            self.serialConsole = None
            return u"Nezdařilo se dostat do U-Bootu."
        except Exception, e: # serial console exception, IOError,...
            logger.warning("[FLASHWORKER] Serial console initialization failed (Exception other than SCError) (routerId=%s). "
                            % self.router.id + str(e))
            self.serialConsole.close()
            self.serialConsole = None
            return u"Nezdařilo se dostat do U-Bootu."
        
        # we are in uboot, move to the next window (with statusbar)
        return ""
    
    def tftp_flash(self):
        """return (int, str), if everything ok, then (0, "")
        else (step which failed, error message)
        """
        
        # set the ip address on local interface
        p = subprocess.Popen(["sudo", "ifconfig", LOCAL_TEST_IFACE, "192.168.10.1"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retCode = p.wait()
        if retCode != 0:
            return (1, "localcmd 'sudo ifconfig %s 192.168.10.1'\nreturn status: %d\n" %
                    (LOCAL_TEST_IFACE, retCode) + p.stdout.read())
        sleep(2)
        
        # issue the uboot commands and parse the console output
        cmdOut = self.serialConsole.exec_("setenv ipaddr 192.168.10.2")
        if cmdOut:
            return (2, "uboot 'setenv ipaddr 192.168.10.2':\n" + cmdOut)
        cmdOut = self.serialConsole.exec_("setenv serverip 192.168.10.1")
        if cmdOut:
            return (3, "uboot 'setenv serverip 192.168.10.1':\n" + cmdOut)
        cmdOut = self.serialConsole.exec_("setenv eth2addr 00:11:22:33:44:55")
        if cmdOut:
            return (4, "uboot 'setenv eth2addr 00:11:22:33:44:55':\n" + cmdOut)
        cmdOut = self.serialConsole.exec_("ping 192.168.10.1", 25) # timeout for ping is 20s
        if not cmdOut.endswith("host 192.168.10.1 is alive\n"):
            return (5, "uboot 'ping 192.168.10.1':\n" + cmdOut)
        cmdOut = self.serialConsole.exec_("tftpboot 0x1000000 nor.bin")
        if cmdOut == "Speed: 1000, full duplex\n*** ERROR: `ethaddr' not set\n" \
                "Speed: 1000, full duplex\n*** ERROR: `eth1addr' not set\n" \
                "eTSEC3 Waiting for PHY auto negotiation to complete......... " \
                "TIMEOUT !\neTSEC3: No link.\nSpeed: 1000, full duplex\n":
            # no link (cable disconnected)
            return (6, "uboot 'tftpboot 0x1000000 nor.bin':\ncable disconnected")
        elif not cmdOut.startswith(
                "Speed: 1000, full duplex\n"
                "Using eTSEC3 device\n"
                "TFTP from server 192.168.10.1; our IP address is 192.168.10.2\n"
                "Filename 'nor.bin'.\n"
                "Load address: 0x1000000\n"
                "Loading: ") \
                or cmdOut.find("\ndone\nBytes transferred = %d (%s hex)\n" %
                               (self.imagesize, hex(self.imagesize)[2:])) == -1:
            return (7, "uboot 'tftpboot 0x1000000 nor.bin':\n" + cmdOut)
        cmdOut = self.serialConsole.exec_("protect off 0xef000000 +0xF80000")
        if cmdOut != "Un-Protected 124 sectors\n":
            return (8, "uboot 'protect off 0xef000000 +0xF80000':\n" + cmdOut)
        # erasing takes ~40sec
        cmdOut = self.serialConsole.exec_("erase 0xef000000 +0xF80000", 90)
        if cmdOut != "\n........................................................................." \
                     "................................................... done\nErased 124 sectors\n":
            return (9, "uboot 'erase 0xef000000 +0xF80000':\n" + cmdOut)
        # copying takes ~40sec
        cmdOut = self.serialConsole.exec_("cp.b 0x1000000 0xef000000 0x$filesize", 80)
        if cmdOut != "Copy to Flash... 9....8....7....6....5....4....3....2....1....done\n":
            return (10, "uboot 'cp.b 0x1000000 0xef000000 0x$filesize':\n" + cmdOut)
        
        # wait until nor -> nand
        self.serialConsole.allow_input()
        self.serialConsole.writeLine("run norboot\n")
        wCounter = 120 # 120 seconds limit, normally it takes 80-90 seconds
        while wCounter and self.serialConsole.inbuf.find("Hit any key to stop autoboot") == -1:
            wCounter -= 1
            sleep(1)
        self.serialConsole.disable_input()
        # set console state to UNDEFINED, it causes the serialConsole to call to_system before tests
        self.serialConsole.state = self.serialConsole.UNDEFINED
        
        if wCounter:
            return (0, "")
        else:
            return (11, "waiting for reboot after nor to nand unpacking timeouted")
    
    @QtCore.pyqtSlot(int)
    def ubootWaitAndTFTP(self, step):
        if step == 0:
            retStr = self.go_to_uboot()
            if retStr:
                # error
                return_code = 1 if self.router.secondChance["NOR"] else 2
                self.router.secondChance["NOR"] = False
                err_msg = retStr
                self.router.error = "error when going to uboot"
                dbErr = not self.router.save()
            else:
                # everything ok
                return_code = 0
                err_msg = ""
                dbErr = False
        else:
            try:
                flash_result = self.tftp_flash()
            except Exception, e:
                logger.warning("[FLASHWORKER] exception when uboot tftp nor flashing: " + repr(e))
                err_msg = u"Chyba konzole: " + unicode(e)
                return_code = 1 if self.router.secondChance["NOR"] else 2
                self.router.secondChance["NOR"] = False
                self.router.error = "Exception in tftp flash procedure. " + repr(e)
            else:
                if flash_result[0] == 0:
                    return_code = 0
                    err_msg = u""
                    self.router.status = self.router.STATUS_FINISHED
                    self.router.error = ""
                else:
                    return_code = 1 if self.router.secondChance["NOR"] else 2
                    self.router.secondChance["NOR"] = False
                    self.router.error = flash_result[1]
                    err_msg = u"someting went wrong in the second stage (TODO specify)"
            
            dbErr = not self.router.save()
        
        # if final error, close the console
        if return_code == 2 and self.serialConsole:
            self.serialConsole.close()
            self.serialConsole = None
        
        self.flashFinished.emit((return_code, err_msg, dbErr))
    
    def testPrepareConsole(self):
        logger.debug("[TESTING] Executing test %d on the router with routerId=%s"
                % (self.router.currentTest, self.router.id))
        
        # create and prepare a serial console connection
        if self.serialConsole is None:
            # find ttyUSBx
            dev = [t for t in os.listdir("/dev/") if t.startswith("ttyUSB")]
            if len(dev) != 1:
                if len(dev) == 0:
                    errMsg = u"Zkontrolujte kabel č. 5, nenašel jsem sériovou konzoli."
                else:
                    errMsg = u"Našel jsem více sériových konzolí, nevím kterou použít."
                return (errMsg, u"Problém sériové konzole.")
            # open the console
            try:
                self.serialConsole = SerialConsole("/dev/" + dev[0])
            except Exception, e:
                return (u"Nezdařilo se otevřít spojení přes konzoli. Zkontrolujte, "
                        u"kabel č. 5 a napájení 7,5V.",
                        u"Problém sériové konzole.")
        
        if self.serialConsole.state != self.serialConsole.OPENWRT:
            try:
                self.serialConsole.to_system()
            except SCError, e:
                logger.warning("[TESTING] Serial console initialization failed (routerId=%s). "
                                % self.router.id + str(e))
                self.serialConsole.close()
                self.serialConsole = None
                return (u"Nezdařila se komunikace se systémem na routru.",
                        u"Problém sériové konzole.")
            except Exception, e: # serial console exception, IOError,...
                logger.warning("[TESTING] Serial console initialization failed (Exception other than SCError) (routerId=%s). "
                                % self.router.id + str(e))
                self.serialConsole.close()
                self.serialConsole = None
                # self.router.testResults[self.router.currentTest] = self.router.TEST_PROBLEM
                return (u"Při komunikaci s routrem přes sériovou konzoli došlo k chybě.",
                        u"Problém sériové konzole.")
    
    @QtCore.pyqtSlot()
    def executeTest(self):
        def report_tests_results():
            # generate test failure list and append it to testResult
            failedTests = [t for t in self.router.testResults.iterkeys() if self.router.testResults[t] != self.router.TEST_OK]
            testsReport = u"<h3>Testy, které selhali</h3>" if failedTests else u"<h3>Všechny testy proběhli správně</h3>"
            for t in failedTests:
                testsReport += TESTLIST[t]['desc'] + u": "
                if self.router.testResults[t] == self.router.TEST_FAIL:
                    testsReport += u"neúspěch"
                elif self.router.testResults[t] == self.router.TEST_PROBLEM:
                    testsReport += u"selhání testu"
                testsReport += u"<br>"
                
            return testsReport
        # end def report_tests_results
        
        # prepare the serial console
        cons_prep_err = self.testPrepareConsole()
        if cons_prep_err:
            self.router.testResults[self.router.currentTest] = self.router.TEST_PROBLEM
            if self.router.testSecondChance:
                self.router.testSecondChance = False
                self.testFinished.emit(self.router.currentTest,
                                       cons_prep_err[0], cons_prep_err[1])
            else:
                self.testFinished.emit(-1, cons_prep_err[0],
                                       report_tests_results())
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
                            traceback.format_exc())
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
                    p_return[1] + "\n-----\n" + p_return[2] + "\n-----\n" + p_return[3])
            
            self.router.currentTest += 1
            if self.router.currentTest >= len(TESTLIST):
                self.serialConsole.close()
                self.serialConsole = None
                nextTest = -1
            else:
                nextTest = self.router.currentTest
        
        if nextTest == -1:
            testResult += report_tests_results()
        
        self.testFinished.emit(nextTest, errMsg, testResult)
    
    @QtCore.pyqtSlot()
    def stepCpldEraser(self):
        logger.debug("[FLASHWORKER] starting cpld erasing step (routerId=%s)" % "not specified") # self.router.id)
        # create a log file
        tmpf_fd, tmpf_path = mkstemp(text=True)
        
        # execute the command
        p_return = self.runCmd((STEP_CPLD_CMD, "-infile", CPLD_ERASE_INFILE, "-logfile", tmpf_path))
        
        # read the log file
        log_content = ""
        tmpr = os.read(tmpf_fd, 1024)
        while tmpr:
            log_content += tmpr
            tmpr = os.read(tmpf_fd, 1024)
        log_content = log_content.strip()
        
        if log_content.endswith("Operation: successful."):
            logger.info("[FLASHWORKER] CPLD erase successful (routerId=%s)" % "not specified") # self.router.id)
            # set self.router.status and error to something reasonable
            # self.router.error = ""
            return_code = 0
            err_msg = ""
        else:
            logger.warning("[FLASHWORKER] CPLD erasing failed, check the cables (routerId=%s)" % "not specified") # self.router.id)
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
    flashStepOneSig = QtCore.pyqtSignal()
    flashStepTwoSig = QtCore.pyqtSignal()
    flashStepThreeSig = QtCore.pyqtSignal()
    runTestSig = QtCore.pyqtSignal()
    checkRouterDbExistsSig = QtCore.pyqtSignal('QString')
    cpldStartEraseSig = QtCore.pyqtSignal()
    tftpBootWaitSig = QtCore.pyqtSignal(int)
    
    STEPS = {
        'START': 0,
        'SCAN': 1,
        'I2C': 2,
        'CPLD': 3,
        'FLASH': 4,
        'TOUBOOT': 5,
        'UBOOTFLASH': 6,
        'BEFORETESTS': 7,
        'CHCKCABLE': 8,
        'ERROR': 9,
        'TESTPREPARE': 10,
        'TESTEXEC': 11,
        'FINISH': 12,
        'ACCESSORIES': 13,
        'ACCTESTS': 14,
        'ACCCPLDERASE': 15
    }
        
    def __init__(self):
        super(Installer, self).__init__()
        
        self.setupUi(self) # create gui
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.blockClose = False
        
        # buttons event listeners
        self.startToScan.clicked.connect(self.simpleMoveToScan)
        self.scanToOne.clicked.connect(self.launchProgramming)
        self.prepareToFirstTest.clicked.connect(self.toNextTest)
        self.chckToStepX.clicked.connect(self.userHasCheckedCables)
        self.errToScan.clicked.connect(self.simpleMoveToScan)
        self.prepTestToRunTest.clicked.connect(self.startPreparedTest)
        self.endToScan.clicked.connect(self.simpleMoveToScan)
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
        self.flashStepOneSig.connect(self.flashWorker.flashStepOne)
        self.flashStepTwoSig.connect(self.flashWorker.flashStepTwo)
        self.flashStepThreeSig.connect(self.flashWorker.flashStepThree)
        self.runTestSig.connect(self.flashWorker.executeTest)
        self.checkRouterDbExistsSig.connect(self.flashWorker.getFlashedRouter)
        self.flashWorker.flashFinished.connect(self.moveToNext)
        self.flashWorker.testFinished.connect(self.toNextTest)
        self.cpldStartEraseSig.connect(self.flashWorker.stepCpldEraser)
        self.tftpBootWaitSig.connect(self.flashWorker.ubootWaitAndTFTP)
        
        self.flashWorker.moveToThread(self.flashThread)
        self.flashThread.start()
        
        # create a database connection, but do not open it, until necessary
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(DB_HOST)
        self.db.setUserName(DB_USER)
        self.db.setPassword(DB_PASS)
        self.db.setDatabaseName(DB_DBNAME)
        
        self.flashingStage = 0 # we start at zero, (start page)
        
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
        self.lineEdit.clear()
        self.lineEdit.setFocus()
        self.scanToOne.setEnabled(True)
        self.stackedWidget.setCurrentIndex(self.STEPS['SCAN'])
    
    @QtCore.pyqtSlot()
    def launchProgramming(self):
        """do the check of scanned id, take it, add to db, and start flashing"""
        barCode = self.lineEdit.text()
        err = False
        if barCode.isEmpty():
            QtGui.QMessageBox.warning(self, u"Chyba",
                    u"Musíte naskenovat čárový kód.")
            self.simpleMoveToScan()
            return
        
        if not serialNumberValidator(barCode):
            QtGui.QMessageBox.warning(self, u"Chyba",
                    u"Neplatný čárový kód, naskenujte ho znovu.")
            self.simpleMoveToScan()
            return
        
        # two possibilities, this id is/is not in the db
        self.scanToOne.setEnabled(False)
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
                    self.flashStepOneSig.emit()
                elif flash_result[0] == 1:
                    i = self.STEPS['CPLD']
                    self.flashStepTwoSig.emit()
                elif flash_result[0] == 2:
                    i = self.STEPS['FLASH']
                    self.flashStepThreeSig.emit()
                elif flash_result[0] == 3:
                    self.tftpBootWaitSig.emit(0)
                    i = self.STEPS['TOUBOOT']
                elif flash_result[0] == 4:
                    i = self.STEPS['BEFORETESTS']
                self.flashingStage = i
            elif flash_result[0] == -1:
                # router already exists
                if QtGui.QMessageBox.question(self, 'Router existuje', flash_result[1],
                        buttons=QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                        defaultButton=QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
                    # start another attempt to flash the router
                    barCode = self.lineEdit.text()
                    self.newRouterAddSig.emit(barCode, True)
                else:
                    # continue with other router
                    self.blockClose = False
                    self.scanToOne.setEnabled(True)
                    self.lineEdit.clear()
                    self.lineEdit.setFocus()
                return
            else:
                # db error, flash_result[0] == -2
                self.blockClose = False
                self.scanToOne.setEnabled(True)
                QtGui.QMessageBox.warning(self, u"Chyba", flash_result[1])
                self.lineEdit.setFocus()
                return
        elif i == self.STEPS['I2C']:
            if flash_result[0] == 0:
                i = self.STEPS['CPLD']
                self.flashingStage = i
                self.flashStepTwoSig.emit()
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['CPLD']:
            if flash_result[0] == 0:
                i = self.STEPS['FLASH']
                self.flashingStage = i
                self.flashStepThreeSig.emit()
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['FLASH']:
            if flash_result[0] == 0:
                i = self.STEPS['TOUBOOT']
                self.flashingStage = i
                self.tftpBootWaitSig.emit(0) # wait for RESET button pressed, then tftpboot and flash
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['TOUBOOT']:
            if flash_result[0] == 0:
                i = self.STEPS['UBOOTFLASH']
                self.tftpBootWaitSig.emit(1)
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']   
        elif i == self.STEPS['UBOOTFLASH']:
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
        logger.debug("[MAIN] switching to the step %d" % i)
    
    @QtCore.pyqtSlot()
    def userHasCheckedCables(self):
        # change the stackedWidget to self.flashingStage and emmit the corresponding signal
        self.stackedWidget.setCurrentIndex(self.flashingStage)
        if self.flashingStage == self.STEPS['I2C']:
            self.flashStepOneSig.emit()
        elif self.flashingStage == self.STEPS['CPLD']:
            self.flashStepTwoSig.emit()
        elif self.flashingStage == self.STEPS['FLASH']:
            self.flashStepThreeSig.emit()
        elif self.flashingStage == self.STEPS['TOUBOOT']:
            self.tftpBootWaitSig.emit(0)
    
    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int, 'QString', 'QString')
    def toNextTest(self, testNum=0, errorText="", testResult=""):
        """current test finished, show given test instructions or "theEnd"
        page if testNum = -1"""
        if errorText:
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
        self.flashStepThreeSig.emit()
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
            QtGui.QMessageBox.critical(self, u"Chyba",
                    u"Musíte naskenovat čárový kód.")
            self.barcodeOnlyTests.clear()
            self.barcodeOnlyTests.setFocus()
            return
        
        if not serialNumberValidator(barCode):
            QtGui.QMessageBox.critical(self, u"Chyba",
                    u"Neplatný čárový kód, naskenujte ho znovu.")
            self.barcodeOnlyTests.clear()
            self.barcodeOnlyTests.setFocus()
            return
        
        # check if this router is in db and set router id and attempt accordingly
        self.toOnlyTests.setEnabled(False)
        self.checkRouterDbExistsSig.emit(barCode)
    
    def closeEvent(self, event):
        if self.blockClose:
            QtGui.QMessageBox.warning(self, u"Chyba",
                                      u"Probíhá flashování, vyčkejte chvíli.")
            event.ignore()
            return
        
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
