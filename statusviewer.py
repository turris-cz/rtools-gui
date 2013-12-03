#!/usr/bin/env python2
# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.


import sys

# router object
from router import Router, DbError, DoesNotExist

# gui related stuff
import uiresources
from PyQt4 import QtGui, QtCore, QtSql
from statusgui import Ui_StatusChecker

# database
DB_HOST = 'localhost'
DB_USER = 'tflasher'
DB_PASS = 'poiuytrewq'
DB_DBNAME = 'turris'


# code


class StatusViewer(QtGui.QWidget, Ui_StatusChecker):
    def __init__(self):
        super(StatusViewer, self).__init__()
        
        self.setupUi(self) # create gui
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.pushButton.clicked.connect(self.showStatus)
        
        # create a database connection, but do not open it, until necessary
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(DB_HOST)
        self.db.setUserName(DB_USER)
        self.db.setPassword(DB_PASS)
        self.db.setDatabaseName(DB_DBNAME)
    
    @QtCore.pyqtSlot()
    def showStatus(self):
        barCodeNum = self.lineEdit.text()
        if barCodeNum.isEmpty():
            statusMsg = u"Musíte naskenovat čárový kód."
        else:
            num, conv = barCodeNum.toLong()
            if conv:
                router = None
                try:
                    router = Router(str(num), readonly=True)
                except DoesNotExist:
                    statusMsg = u"Router s id %s neexistuje." % str(num)
                except DbError, e:
                    statusMsg = e.message
                
                if router:
                    statusMsg = self.createMessage(router)
                else:
                    statusMsg = u"Router s id %s neexistuje v databázi. Pravděpodobně ješte nebyl naflashován." % str(num)
            else:
                statusMsg = u"Neplatný čárový kód, naskenujte ho znovu."
        
        self.lineEdit.clear()
        self.lineEdit.setFocus()
        self.outBox.setText(statusMsg)
    
    def createMessage(self, router):
        if router.status == router.STATUS_FINISHED:
            statusMsg = u"Router s id %s byl úspěšně kompletně naflashován." % router.id
        elif router.error:
            statusMsg = u"Router s id %s nebyl naflashován úspěšně." % router.id \
                        + "chyba:<br>" + router.error
        else:
            statusMsg = u"Router s id %s se asi flashuje." % router.id
        return statusMsg
    
    def closeEvent(self, event):
        # close the database
        if self.db.isOpen():
            self.db.close()
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    widget = StatusViewer()
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
