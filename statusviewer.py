#!/usr/bin/env python2
# coding=utf-8

# author Pavol Otto <pavol.otto@nic.cz>
# copyright 2013 CZ.NIC, z.s.p.o.


import sys
from os import path

# database
from ZODB.config import databaseFromURL as zodb
# router object
from router import Router

# gui related stuff
import uiresources
from PyQt4 import QtGui, QtCore
from statusgui import Ui_StatusChecker

# configuration
ZODB_CONFIG = path.join(path.split(path.join(".", __file__))[0],'zodb.conf')


# code

class StatusViewer(QtGui.QWidget, Ui_StatusChecker):
    def __init__(self, routerList):
        super(StatusViewer, self).__init__()
        
        self.routerList = routerList
        self.setupUi(self) # create gui
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.pushButton.clicked.connect(self.showStatus)
    
    @QtCore.pyqtSlot()
    def showStatus(self):
        barCodeNum = self.lineEdit.text()
        if barCodeNum.isEmpty():
            statusMsg = u"Musíte naskenovat čárový kód."
        else:
            num, conv = barCodeNum.toLong()
            if conv:
                print type(self.routerList)
                router = self.routerList.get(num)
                if router:
                    statusMsg = self.createMessage(router)
                else:
                    statusMsg = u"Router s id %d neexistuje v databázi. Pravděpodobně ješte nebyl naflashován." % num
            else:
                statusMsg = u"Neplatný čárový kód, naskenujte ho znovu."
        
        self.lineEdit.clear()
        self.lineEdit.setFocus()
        self.outBox.setText(statusMsg)
    
    def createMessage(self, router):
        if router.status == Router.STATUS_FINISHED:
            statusMsg = u"Router s id %d byl úspěšně kompletně naflashován." % router.id
        elif router.error:
            statusMsg = u"Rouer s id %d nebyl naflashován úspěšně." % router.id
        else:
            statusMsg = u"Router s id %d se asi flashuje." % router.id


def main():
    # database connection/initialization
    db = zodb(ZODB_CONFIG)
    conn = db.open()
    dbroot = conn.root()
    if not dbroot.has_key('routers'):
        dbroot['routers'] = OOBTree()
    
    app = QtGui.QApplication(sys.argv)
    widget = StatusViewer(dbroot['routers'])
    widget.show()
    
    # TODO échec de la communication
    #if not widget.db:
    #    widget.modalMessage(CONN_ERR_MSG + DB_FAIL_CLOSE_APP)
    #    sys.exit(1)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
