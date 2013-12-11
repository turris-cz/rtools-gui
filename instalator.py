#!/usr/bin/env python2
# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.
# licensed under the BSD license

#python modules
import logging
import subprocess
import sys
import os
from tempfile import mkstemp
from shutil import copy

# gui related stuff
from PyQt4 import QtGui, QtCore, QtSql
from gui import uiresources
from gui.gui_installer import Ui_Installer

# router object
from router import Router, DbError, DuplicateKey, DoesNotExist

# tests
from router_tests import TESTLIST

# settings
STEP_ONE_CMD = "/home/palko/Projects/router/instalator/mock/i2cflasher"
STEP_TWO_CMD = "/home/palko/Projects/router/instalator/mock/lattice"
STEP_TWO_INFILE = "/home/palko/neexistujucialejetojedno"
STEP_THREE_CMD = "/home/palko/Projects/router/instalator/mock/codewarrior"
STEP_THREE_LOGFILE = "/home/palko/Projects/router/instalator/mock/session.log"
LOG_BACKUP_CMD = "/bin/true" # "/home/turris/backup_logs.sh"

# database
DB_HOST = 'localhost'
DB_USER = 'tflasher'
DB_PASS = 'poiuytrewq'
DB_DBNAME = 'turris'

#logging
LOGLEVEL = logging.NOTSET # log everyting

logger = logging.getLogger('installer')
logger.root.setLevel(LOGLEVEL)
nanlogsdir = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                   "nandnorlogs")
logfile = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                   "logdir/flasher.log")
fh = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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
    testFinished = QtCore.pyqtSignal(int)
    
    def __init__(self):
        super(FlashingWorker, self).__init__()
        self.router = None
    
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
    
    @QtCore.pyqtSlot()
    def flashStepOne(self):
        logger.debug("[FLASHWORKER] starting first step (routerId=%s)" % self.router.id)
        p_return = self.runCmd((STEP_ONE_CMD, self.router.id))
        
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
            err_msg = u"Flashování I2C zlyhalo, zkontrolujte připojené kabely."
        else:
            logger.warning("[FLASHWORKER] I2C step failed definitely (routerId=%s)" % self.router.id)
            self.router.error = p_return[1]
            return_code = 2
            err_msg = u"Flashování I2C zlyhalo."
        
        dbErr = not self.router.save()
        
        self.flashFinished.emit((return_code, err_msg, dbErr))
    
    @QtCore.pyqtSlot()
    def flashStepTwo(self):
        logger.debug("[FLASHWORKER] starting second step (routerId=%s)" % self.router.id)
        # create a log file
        tmpf_fd, tmpf_path = mkstemp(text=True)
        
        # execute the command
        p_return = self.runCmd((STEP_TWO_CMD, "-infile", STEP_TWO_INFILE, "-logfile", tmpf_path))
        
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
            err_msg = u"Flashování CPLD zlyhalo, zkontrolujte připojené kabely."
        else:
            logger.warning("[FLASHWORKER] CPLD step failed definitely (routerId=%s)" % self.router.id)
            self.router.error = log_content
            return_code = 2
            err_msg = u"Flashování CPLD zlyhalo."
        
        # close and delete the log file
        os.close(tmpf_fd)
        os.remove(tmpf_path)
        
        dbErr = not self.router.save()
        
        self.flashFinished.emit((return_code, err_msg, dbErr))
    
    @QtCore.pyqtSlot()
    def flashStepThree(self):
        logger.debug("[FLASHWORKER] starting third step (routerId=%s)" % self.router.id)
        p_return = self.runCmd(("/bin/bash", STEP_THREE_CMD))
        
        # copy and send log_backup
        persistentLog = os.path.join(nanlogsdir, "%s-%d-%s.log" %
                (self.router.id, self.router.attempt,
                 self.router.secondChance['FLASH'] and "0" or "1"))
        try:
            copy(STEP_THREE_LOGFILE, persistentLog)
            self.runCmd((LOG_BACKUP_CMD, persistentLog))
        except Exception: # IOError, OSError, ...?
            pass
        
        return_code = 0
        err_msg = ""
        
        try:
            with open(STEP_THREE_LOGFILE, "r") as fh:
                logtext = fh.read()
        except IOError:
            logger.critical("[FLASHWORKER] Could not read codewarrior session.log, application error")
            logtext = "Error"
            # TODO maybe close the application now
        
        cableDisconnected = logtext.find("Cable disconnected") >= 0
        if cableDisconnected and self.router.secondChance['FLASH']:
            # cable disconnected,
            logger.warning("[FLASHWORKER] FLASH step failed, check the cables (routerId=%s)" % self.router.id)
            self.router.secondChance['FLASH'] = False
            self.router.error = "Flashing exited with \"Cable disconnected\" in session.log\n"
                                # TODO copy session.log
            
            return_code = 1
            err_msg = u"Flashování Flash pamětí zlyhalo, zkontrolujte připojené kabely."
        elif logtext.find("Error") >= 0 or (cableDisconnected and not self.router.secondChance['FLASH']):
            logger.warning("[FLASHWORKER] FLASH step failed definitely (routerId=%s)" % self.router.id)
            self.router.error = "Flashing exited with \"Error\" in session.log"
                                # TODO copy session.log
            return_code = 2
            err_msg = u"Flashování NAND a NOR zlyhalo."
        else:
            # TODO is there a Diagnose Succeeded string?
            logger.info("[FLASHWORKER] FLASH step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_FINISHED
            self.router.error = ""
        
        dbErr = not self.router.save()
        
        self.flashFinished.emit((return_code, err_msg, dbErr))
    
    @QtCore.pyqtSlot()
    def executeTest(self):
        logger.debug("[TESTING] Executing test %d on the router with routerId=%s"
                % (self.router.currentTest, self.router.id))
        
        # run the test
        p_return = self.runCmd(TESTLIST[self.router.currentTest]['cmd'])
        
        # save to db the test result p_return[0]
        self.router.saveTestResult(p_return[0])
        
        self.router.currentTest += 1
        if self.router.currentTest >= len(TESTLIST):
            nextTest = -1
        else:
            nextTest = self.router.currentTest
        
        self.testFinished.emit(nextTest)


class Installer(QtGui.QWidget, Ui_Installer):
    """Installer GUI application for flashing the Turris routers"""
    
    newRouterAddSig = QtCore.pyqtSignal('QString', bool)
    flashStepOneSig = QtCore.pyqtSignal()
    flashStepTwoSig = QtCore.pyqtSignal()
    flashStepThreeSig = QtCore.pyqtSignal()
    runTestSig = QtCore.pyqtSignal()
    
    STEPS = {
        'START': 0,
        'SCAN': 1,
        'I2C': 2,
        'CPLD': 3,
        'RESET': 4,
        'FLASH': 5,
        'SUCCESS': 6,
        'CHCKCABLE': 7,
        'ERROR': 8,
        'TESTPREPARE': 9,
        'TESTEXEC': 10,
        'FINISH': 11
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
        self.resetToThree.clicked.connect(self.routerReset)
        self.finalToTest.clicked.connect(self.toNextTest)
        self.chckToStepX.clicked.connect(self.userHasCheckedCables)
        self.errToScan.clicked.connect(self.simpleMoveToScan)
        self.prepTestToRunTest.clicked.connect(self.startPreparedTest)
        self.endToScan.clicked.connect(self.simpleMoveToScan)
        
        # start a second thread which will do the flashing
        self.flashWorker = FlashingWorker()
        self.flashThread = QtCore.QThread()
        
        self.newRouterAddSig.connect(self.flashWorker.addNewRouter)
        self.flashStepOneSig.connect(self.flashWorker.flashStepOne)
        self.flashStepTwoSig.connect(self.flashWorker.flashStepTwo)
        self.flashStepThreeSig.connect(self.flashWorker.flashStepThree)
        self.runTestSig.connect(self.flashWorker.executeTest)
        self.flashWorker.flashFinished.connect(self.moveToNext)
        self.flashWorker.testFinished.connect(self.toNextTest)
        
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
            self.modalMessage(u"Musíte naskenovat čárový kód.")
            self.simpleMoveToScan()
            return
        
        if not serialNumberValidator(barCode):
            self.modalMessage(u"Neplatný čárový kód, naskenujte ho znovu.")
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
                self.modalMessage(flash_result[1])
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
                i = self.STEPS['RESET']
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        elif i == self.STEPS['FLASH']:
            if flash_result[0] == 0:
                self.flashingStage = 0
                i = self.STEPS['SUCCESS']
            elif flash_result[0] == 1:
                self.tmpErrMsg.setText(flash_result[1])
                i = self.STEPS['CHCKCABLE']
            else:
                i = self.STEPS['ERROR']
        
        if i in (self.STEPS['SUCCESS'], self.STEPS['ERROR']):
            # unblock the possibility to close the app
            self.blockClose = False
        
        # change the stackedWidget index
        self.stackedWidget.setCurrentIndex(i)
        logger.debug("[MAIN] switching to the step %d (step 6 is error page)" % i)
    
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
    
    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int)
    def toNextTest(self, testNum = 0):
        """current test finished, show given test instructions or "theEnd"
        page if testNum = -1"""
        
        if testNum < 0:
            nextPage = self.STEPS['FINISH']
        else:
            nextPage = self.STEPS['TESTPREPARE']
            self.testInstructions.setText(TESTLIST[testNum]['desc'])
        
        self.stackedWidget.setCurrentIndex(nextPage)
    
    @QtCore.pyqtSlot()
    def startPreparedTest(self):
        self.runTestSig.emit()
        self.stackedWidget.setCurrentIndex(self.STEPS['TESTEXEC'])
    
    @QtCore.pyqtSlot()
    def routerReset(self):
        self.flashingStage = self.STEPS['FLASH']
        self.flashStepThreeSig.emit()
        self.stackedWidget.setCurrentIndex(self.flashingStage)
    
    def closeEvent(self, event):
        if self.blockClose:
            self.modalMessage(u"Probíhá flashování, vyčkejte chvíli.")
            event.ignore()
            return
        
        # close the database
        if self.db.isOpen():
            self.db.close()
        self.flashThread.quit()
        event.accept()
    
    def modalMessage(self, msg):
        # FIXME refactor using QMessageBox.information
        mBox = QtGui.QMessageBox(self)
        mBox.setWindowTitle(u"Chyba")
        mBox.setText(msg)
        # StandardButtons=QtGui.QMessageBox.Ok
        mBox.show()
        return mBox.exec_()


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
