# -*- coding: utf8 -*-

import time

from workflow.base import Base, BaseWorker, spawnPexpectSerialConsole
from workflow.tests.omnia import SerialNumberTest
from application import settings


class EnterUboot(Base):
    _name = "ENTER UBOOT"

    @property
    def instructions(self):
        return """
            <h3>Aktualizace systému</h3>
            <ul>
                <li>Ujistěte se, že do usb portů není zapojeno žándé zařízení.</li>
                <li>Vložte flash disk se záchraným systémem do routeru.</li>
                <li>Připojte napájení k routeru.</li>
                <li>Klikněte na tlačítko OK.</li>
                <li>Stiskněte tlačítko reset na routeru.</li>
            <ul>
        """

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):
        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)
            self.setTitle.emit(u"!!! Stiskněte tlačítko reset na routeru !!!")
            self.expect(exp, "U-Boot")
            self.setTitle.emit(None)
            self.progress.emit(50)
            exp.delaybeforesend = 0

            # get into uboot shell
            # unfortunatelly can't wait for "Hit any key to stop autoboot" msg (too small delay)
            # so a several new line commands will be sent there

            tries = 20  # 10s shall be enough
            while True:
                time.sleep(0.5)
                exp.sendline('\n')
                res = self.expect(exp, [r'.*[\n\r]+=>.*', r'.+'] if tries > 0 else r'=>')
                if res == 0:
                    break
                else:
                    tries -= 1

            self.progress.emit(100)

            return True


class UsbFlash(Base):
    _name = "USB FLASH"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):
        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)
            exp.sendline("setenv rescue 3")
            time.sleep(0.5)
            exp.sendline("run rescueboot")
            self.progress.emit(5)

            # flashing
            self.expect(exp, 'Mode: Reflash...', timeout=150)
            self.progress.emit(40)

            self.expect(exp, 'Reflash succeeded.', timeout=150)
            self.progress.emit(70)

            self.expect(exp, 'Router Turris successfully started.', timeout=150)
            self.progress.emit(90)

            # read the git version
            self.expectSystemConsole(exp)
            self.progress.emit(100)

            return True


class Halt(Base):
    _name = "HALT"

    def createWorker(self):
        return self.Worker()

    class Worker(BaseWorker):
        def perform(self):
            exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
            self.progress.emit(1)

            self.expectSystemConsole(exp)
            self.progress.emit(50)

            # halt properly
            exp.sendline("halt")
            self.expect(exp, "reboot: System halted")
            self.progress.emit(100)

            return True


TESTS = (
    EnterUboot(),
    UsbFlash(),
    SerialNumberTest(),
    Halt(),
)
