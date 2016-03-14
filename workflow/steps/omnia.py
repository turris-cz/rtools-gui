import pexpect
import sys

from PyQt5 import QtCore

from workflow.base import Base, BaseWorker
from application import settings


class Sample(Base):

    def __init__(self, name):
        self._name = name

    def getWorker(self):
        return SampleWorker(settings.STEP_SETTINGS['sample']['script_path'])

class SampleWorker(BaseWorker):
    def __init__(self, path):
        super(SampleWorker, self).__init__()
        self.path = path

    @QtCore.pyqtSlot()
    def start(self):
        child = pexpect.spawn(self.path, logfile=sys.stdout)
        child.expect("Phase 1")
        self.progress.emit(1)
        child.expect("Phase 2")
        self.progress.emit(20)
        child.expect("Phase 3")
        self.progress.emit(20)
        child.expect(pexpect.EOF)
        self.finished.emit(True)


WORKFLOW = (
    Sample("POWER"),
    Sample("ATSHA"),
    Sample("UBOOT"),
    Sample("REBOOT"),
    Sample("REFLASH"),
    Sample("RTC"),
)
