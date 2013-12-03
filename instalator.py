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

# gui related stuff
import uiresources
from PyQt4 import QtGui, QtCore, QtSql
from gui import Ui_Installer

# router object
from router import Router, DbError

# settings
STEP_ONE_CMD = "/home/palko/Projects/router/instalator/i2cflasher"
STEP_TWO_CMD = "/home/palko/Projects/router/instalator/lattice mock/lattice"
STEP_TWO_INFILE = "/home/palko/neexistujucialejetojedno"
STEP_THREE_CMD = "/home/palko/Projects/router/instalator/codewarrior"

# database
DB_HOST = 'localhost'
DB_USER = 'tflasher'
DB_PASS = 'poiuytrewq'
DB_DBNAME = 'turris'

#logging
LOGLEVEL = logging.NOTSET # log everyting

logger = logging.getLogger('installer')
logger.root.setLevel(LOGLEVEL)
fh = logging.FileHandler("flasher.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.root.addHandler(fh)


# code


class FlashingWorker(QtCore.QObject):
    """Flashing Worker which run given commands and returns the status of the
    flashing process.
    """
    
    # tuple (int code, str msg) code 0 - ok, 1 - error which leads to the 'error' page, 2 - error which shows the modal dialog
    flashFinished = QtCore.pyqtSignal(tuple)
    
    def __init__(self):
        super(FlashingWorker, self).__init__()
        self.router = None
    
    def runCmd(self, cmdWithArgs):
        logger.info("[FLASHWORKER] start flashing (command: `%s`)" % " ".join(cmdWithArgs))
        # TODO self.p - in order to be able to kill the process after some time
        p = subprocess.Popen(cmdWithArgs, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retCode = p.wait()
        stdOut = p.stdout.read() # TODO handle the case of big outputs in a better way
        return (retCode, stdOut if len(stdOut) < 1001 else (stdOut[:1000] + "... output truncated"))
    
    @QtCore.pyqtSlot('QString')
    def addNewRouter(self, routerId):
        return_code = 0
        err_msg = ""
        
        try:
            self.router = Router(str(routerId)) # create new or fetch info about old
            if self.router.status != self.router.STATUS_START or self.router.error:
                return_code = 2
                err_msg = u"Tento router už byl naflashován, vezměte další."
        except DbError, e:
            return_code = 2
            err_msg = e.message
        
        self.flashFinished.emit((return_code, err_msg))
    
    @QtCore.pyqtSlot()
    def flashStepOne(self):
        logger.debug("[FLASHWORKER] starting first step (routerId=%s)" % self.router.id)
        p_return = self.runCmd((STEP_ONE_CMD, self.router.id))
        return_code = 0
        err_msg = ""
        if p_return[0] == 0:
            logger.info("[FLASHWORKER] second step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_I2C
        else:
            logger.warning("[FLASHWORKER] second step failed (routerId=%s)" % self.router.id)
            self.router.error = p_return[1]
            return_code = 1
            err_msg = u"Flashování I2C zlyhalo."
        
        self.router.save() # TODO handle db error
        
        self.flashFinished.emit((return_code, err_msg))
    
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
            logger.info("[FLASHWORKER] second step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_CPLD
        else:
            logger.warning("[FLASHWORKER] second step failed (routerId=%s)" % self.router.id)
            self.router.error = log_content
            return_code = 1
            err_msg = u"Flashování CPLD zlyhalo."
        
        # close and delete the log file
        os.close(tmpf_fd)
        os.remove(tmpf_path)
        
        self.router.save() # TODO handle db error
        
        self.flashFinished.emit((return_code, err_msg))
    
    @QtCore.pyqtSlot()
    def flashStepThree(self):
        logger.debug("[FLASHWORKER] starting third step (routerId=%s)" % self.router.id)
        p_return = self.runCmd((STEP_THREE_CMD,))
    
        return_code = 0
        err_msg = ""
        if p_return[0] == 0:
            logger.info("[FLASHWORKER] third step successful (routerId=%s)" % self.router.id)
            self.router.status = self.router.STATUS_FINISHED
        else:
            logger.warning("[FLASHWORKER] third step failed (routerId=%s)" % self.router.id)
            self.router.error = "Flashing exited with return status %d\n" % p_return[0] + \
                                "stdout + stderr:\n" + p_return[1]
            return_code = 1
            err_msg = u"Flashování NAND a NOR zlyhalo."
        
        self.router.save() # TODO handle db error
        
        self.flashFinished.emit((return_code, err_msg))


class Installer(QtGui.QWidget, Ui_Installer):
    """Installer GUI application for flashing the Turris routers"""
    
    newRouterAddSig = QtCore.pyqtSignal('QString')
    flashStepOneSig = QtCore.pyqtSignal()
    flashStepTwoSig = QtCore.pyqtSignal()
    flashStepThreeSig = QtCore.pyqtSignal()
    
    def __init__(self):
        super(Installer, self).__init__()
        
        self.setupUi(self) # create gui
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.blockClose = False
        
        # buttons event listeners
        self.startToOne.clicked.connect(self.moveToNext)
        self.oneToTwo.clicked.connect(self.moveToNext)
        self.finalToStart.clicked.connect(self.moveToNext)
        self.errToStart.clicked.connect(self.moveToNext)
        
        # start a second thread which will do the flashing
        self.flashWorker = FlashingWorker()
        self.flashThread = QtCore.QThread()
        
        self.newRouterAddSig.connect(self.flashWorker.addNewRouter)
        self.flashStepOneSig.connect(self.flashWorker.flashStepOne)
        self.flashStepTwoSig.connect(self.flashWorker.flashStepTwo)
        self.flashStepThreeSig.connect(self.flashWorker.flashStepThree)
        self.flashWorker.flashFinished.connect(self.moveToNext)
        
        self.flashWorker.moveToThread(self.flashThread)
        self.flashThread.start()
        
        # create a database connection, but do not open it, until necessary
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(DB_HOST)
        self.db.setUserName(DB_USER)
        self.db.setPassword(DB_PASS)
        self.db.setDatabaseName(DB_DBNAME)
    
    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(tuple)
    def moveToNext(self, flash_result = None):
        i = self.stackedWidget.currentIndex()
        # if going to step 1, clear the lineEdit
        if i == 0:
            self.lineEdit.clear()
            self.lineEdit.setFocus()
            self.oneToTwo.setEnabled(True)
            i = 1
        elif i == 1:
            if flash_result:
                # called from flashThread
                if flash_result[0] == 0:
                    i = 2
                    self.flashStepOneSig.emit()
                else:
                    self.blockClose = False
                    self.oneToTwo.setEnabled(True)
                    self.modalMessage(flash_result[1])
                    self.lineEdit.clear()
                    self.lineEdit.setFocus()
                    return
            else:
                # clicked on the button and barcode scanned
                routerId = self.barCodeVerify()
                if routerId < 0:
                    self.lineEdit.clear()
                    self.lineEdit.setFocus()
                    return
                # two possibilities, this id is/is not in the db
                self.oneToTwo.setEnabled(False)
                self.blockClose = True
                self.newRouterAddSig.emit(str(routerId))
        elif i == 2:
            if flash_result[0] == 0:
                i = 3
                self.flashStepTwoSig.emit()
            else: # flash_result[0] == 1
                i = 6
                # TODO show flash_result[1] on errorPage
        elif i == 3:
            if flash_result[0] == 0:
                i = 4
                self.flashStepThreeSig.emit()
            else: # flash_result[0] == 1
                i = 6 # error page
                # TODO show flash_result[1] on errorPage
        elif i == 4:
            if flash_result[0] == 0:
                i = 5
            else:
                i = 6
                # TODO show flash_result[1] on errorPage
        else:
            # go to the start screen
            i = 0
        
        if i > 4:
            # unblock the possibility to close the app
            self.blockClose = False
        
        # change the stackedWidget index
        self.stackedWidget.setCurrentIndex(i)
        
        logger.debug("[MAIN] switching to the step %d (step 6 is error page)" % i)
    
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
    
    def barCodeVerify(self):
        """barCodeVerify() -> long
        Return integer representation of scanned code or less than zero if the code is invalid.
        """
        barCodeNum = self.lineEdit.text()
        if barCodeNum.isEmpty():
            self.modalMessage(u"Musíte naskenovat čárový kód.")
            return -1
        num, conv = barCodeNum.toLong()
        if not conv:
            self.modalMessage(u"Neplatný čárový kód, naskenujte ho znovu.")
            return -2
        return num
    
    def modalMessage(self, msg):
        mBox = QtGui.QMessageBox(self)
        mBox.setWindowTitle(u"Chyba")
        mBox.setText(msg)
        # StandardButtons=QtGui.QMessageBox.Ok)
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
