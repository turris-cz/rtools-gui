#!/usr/bin/env python2
# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.

#python modules
import logging
import subprocess
import sys
from os import path

# gui related stuff
import uiresources
from PyQt4 import QtGui, QtCore
from gui import Ui_Installer

# database
import transaction
from BTrees.OOBTree import OOBTree
from ZODB.config import databaseFromURL as zodb
from ZODB.POSException import ConflictError
from ZEO.Exceptions import ClientDisconnected

# router object
from router import Router

# settings
I2C_SCRIPT = path.join(path.split(path.join(".", __file__))[0],'i2cflasher')
ZODB_CONFIG = path.join(path.split(path.join(".", __file__))[0],'zodb.conf')
LOGLEVEL = logging.NOTSET # log everyting


CONN_ERR_MSG = u"Připojení k databázi zlyhalo. Zkontrolujte připojení k síti."
DB_FAIL_CLOSE_APP = u" Aplikace se ukončí, spusťte ji znovu po ověření internetového připojení."


#logging
logger = logging.getLogger('installer')
logger.root.setLevel(LOGLEVEL)
fh = logging.FileHandler("out.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.root.addHandler(fh)
#consoleHandler = logging.StreamHandler()
#logger.addHandler(consoleHandler)


# code

class FlashingThread(QtCore.QThread):
    def __init__(self, parent=None):
        super(FlashingThread, self).__init__(parent)
        self.parent = parent
        self.retstat = -1
        self.scriptMsg = ""
        # self.signal = QtCore.SIGNAL("flashed")
    
    def run(self):
        logger.info("[I2C] start flashing router %s" % str(self.parent.router))
        
        p = subprocess.Popen(I2C_SCRIPT + " '" + str(self.parent.router.id) + "'",
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             shell=True)
        self.retstat = p.wait()
        if self.retstat > 0:
            logger.warn("[I2C] flashing has failed with exitcode %d" % self.retstat)
            self.scriptMsg = p.stdout.read()
        else:
            logger.info("[I2C] router %s flashed successfully" % str(self.parent.router))


class Installer(QtGui.QWidget, Ui_Installer):
    def __init__(self, routerList):
        super(Installer, self).__init__()
        
        self.setupUi(self) # create gui
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.blockClose = False
        self.routerList = routerList
        self.router = None
        
        # event listeners
        # next step buttons
        self.startToOne.clicked.connect(self.moveToNext)
        self.oneToTwo.clicked.connect(self.moveToNext)
        self.twoToThree.clicked.connect(self.moveToNext)
        self.threeToFinal.clicked.connect(self.moveToNext)
        self.finalToStart.clicked.connect(self.moveToNext)
        self.errToStart.clicked.connect(self.moveToNext)
        # error buttons
        self.twoToErr.clicked.connect(self.moveToError)
        self.threeToErr.clicked.connect(self.moveToError)
    
    @QtCore.pyqtSlot()
    def moveToNext(self):
        i = self.stackedWidget.currentIndex()
        # if going to step 1, clear the lineEdit
        if i == 0:
            self.lineEdit.clear()
        elif i == 1:
            routerId = self.barCodeVerify()
            if routerId < 0:
                self.lineEdit.clear()
                self.lineEdit.setFocus()
                return
            # two possibilities, this id is/is not in the db
            flashedFlag = False
            transaction.begin()
            if self.routerList.has_key(routerId):
                flashedFlag = True
                # TODO add possibility to continue with partially flashed router without error
                # router = self.routerList[routerId]
            else:
                self.router = Router(routerId)
                self.routerList[routerId] = self.router
                try:
                    transaction.commit()
                except ConflictError:
                    transaction.abort()
                    flashedFlag = True
                    self.router = None
                except ClientDisconnected, e:
                    transaction.abort()
                    self.modalMessage(CONN_ERR_MSG)
                    return
            if flashedFlag:
                self.modalMessage(u"Tento router už byl naflashován, vezměte další.")
                self.lineEdit.clear()
                self.lineEdit.setFocus()
                return
        elif i == 2:
            self.blockClose = False
            # get returnCode and msg
            if self.flashThread.retstat > 0:
                logger.warn("[MAIN] i2c flashing has failed with exitcode %d" % self.flashThread.retstat)
                self.router.error = self.flashThread.scriptMsg or "Unknown error"
                self.modalMessage(u"Flashování I2C zlyhalo s kódem %d" % self.flashThread.retstat)
                self.stackedWidget.setCurrentIndex(6)
            else:
                self.router.status = Router.STATUS_I2C
            self.flashThread = None
        elif i == 3:
            self.router.status = Router.STATUS_CPLD
        elif i == 4:
            self.router.status = Router.STATUS_FINISHED
        
        # change the stackedWidget index
        if i == 0:
            i += 1
        elif i > 4:
            i = 0
        elif self.router.error:
            i = 6
        else:
            i += 1
        
        self.stackedWidget.setCurrentIndex(i)
        
        logger.debug("[MAIN] switching to %d step" % i)
        # if 1, set focus to the lineEdit
        if i == 1:
             self.lineEdit.setFocus()
        # if 2, start the subprocess
        elif i == 2:
            self.blockClose = True
            self.flashThread = FlashingThread(self)
            self.flashThread.finished.connect(self.moveToNext)
            self.flashThread.start()
        elif i == 5 or i == 6:
            transaction.commit()
    
    def moveToError(self):
        i = self.stackedWidget.currentIndex()
        logger.warn("[MAIN] Error during flashing step %d" % (i - 1))
        self.router.error = "Error during flashing step %d" % (i - 1)
        transaction.commit()
        self.stackedWidget.setCurrentIndex(6)
    
    
    def closeEvent(self, event):
        if self.blockClose:
            self.modalMessage(u"Probíhá flashování, zkuste za chvíli.")
            event.ignore()
            return
        
        transaction.commit()
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
    logger.info("[MAIN] starting application")
    # database connection/initialization
    logger.info("[MAIN] connecting to the database...")
    db = zodb(ZODB_CONFIG)
    conn = db.open()
    dbroot = conn.root()
    if not dbroot.has_key('routers'):
        dbroot['routers'] = OOBTree()
    
    app = QtGui.QApplication(sys.argv)
    widget = Installer(dbroot['routers'])
    widget.show()
    
    # TODO échec de la communication
    #if not widget.db:
    #    widget.modalMessage(CONN_ERR_MSG + DB_FAIL_CLOSE_APP)
    #    sys.exit(1)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
