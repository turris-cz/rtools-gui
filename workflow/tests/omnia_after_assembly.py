# -*- coding: utf8 -*-

import pexpect
import time

from application import settings

from workflow.base import Base, BaseWorker, spawnPexpectSerialConsole
from workflow.tests.omnia import (
    SerialNumberTest, MiniPCIeTest, ClockTest
)
from workflow.tests.omnia_distributors_reflash_system import Halt


class UsbFlash(Base):
    _name = "USB FLASH"

    @property
    def instructions(self):
        return """
            <h3>%(test_name)s</h3>
            <p>Před tím, než budete pokračovat:</p>
            <ul>
                <li>Připojte UART kabel k routeru.</li>
                <li>Připojte USB s medkitem k routeru.</li>
                <li>Připojte napájení napájení do routeru.</li>
            </ul>
        """ % dict(test_name=self._name)

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):

        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])

            self.setTitle.emit(u"!!! Stiskněte tlačítko reset na routeru !!!")
            while True:
                exp.sendline('\n')
                res = self.expect(exp, [r'.*[\n\r]+=>.*', r'.+', pexpect.TIMEOUT])
                if res == 0:
                    break
                time.sleep(1)
            self.setTitle.emit(None)
            self.progress.emit(10)

            # perform commands
            exp.sendline("setenv rescue 3")
            self.progress.emit(20)
            time.sleep(0.1)
            exp.sendline("run rescueboot")
            self.progress.emit(30)
            time.sleep(0.1)

            self.expect(exp, 'Mode: Reflash...', timeout=150)
            self.progress.emit(40)

            self.expect(exp, 'Reflash succeeded.', timeout=150)
            self.progress.emit(60)

            self.expect(exp, 'Router Turris successfully started.', timeout=150)
            self.progress.emit(80)

            self.expectSystemConsole(exp)
            self.progress.emit(100)

            return True


TESTS = (
    UsbFlash(),
    SerialNumberTest(),
    MiniPCIeTest("3-01", 0x01),
    MiniPCIeTest("3-02", 0x02),
    ClockTest(),
    Halt(),
)
