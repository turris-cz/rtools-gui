# -*- coding: utf8 -*-

import os
import pexpect

from application import settings
from utils import md5File
from workflow.base import Base, BaseWorker


class Beacon(Base):
    _name = "BEACON"

    @property
    def instructions(self):
        return """
            <h3>Aktualizace bootloader</h3>
            <ul>
                <li>Zkontrolujte, že máte do počítače připojený eth dongle.</li>
                <li>Zkontrolujte, máte do eth donglu připojený kabel.</li>
                <li>Připojte druhý konec kabelu do zdířky WAN</li>
                <li>Připojte napájení k routeru.</li>
                <li>Klikněte na tlačítko OK.</li>
                <li>Stiskněte tlačítko reset na routeru.</li>
            <ul>
        """

    def createWorker(self):
        return self.Worker(
            settings.PATHS['uboot_reflash']['beacon'],
            settings.PATHS['uboot_reflash']['tty'],
        )

    class Worker(BaseWorker):
        def __init__(self, beacon_path, tty_path):
            super(Beacon.Worker, self).__init__()
            self.beacon_path = beacon_path
            self.tty_path = tty_path

        def perform(self):
            self.progress.emit(1)
            self.setTitle.emit(u"!!! Stiskněte tlačítko reset na routeru !!!")
            self.expectLocalCommand("%s %s" % (self.beacon_path, self.tty_path))
            self.setTitle.emit(None)
            self.progress.emit(100)

            return True


class LoadUboot(Base):
    _name = "UBOOT LOAD"

    def createWorker(self):
        return self.Worker(
            settings.PATHS['uboot_reflash']['load_script'],
            settings.PATHS['uboot_reflash']['kwboot'],
            settings.PATHS['uboot_reflash']['uart_uboot'],
            settings.PATHS['uboot_reflash']['tty'],
        )

    class Worker(BaseWorker):
        def __init__(self, load_script_path, kwboot_path, uart_uboot_path, tty_path):
            super(LoadUboot.Worker, self).__init__()
            self.load_script_path = load_script_path
            self.kwboot_path = kwboot_path
            self.uart_uboot_path = uart_uboot_path
            self.tty_path = tty_path

        def perform(self):
            self.progress.emit(1)
            exp = self.expectStartLocalCommand("%s %s %s %s" % (
                self.load_script_path, self.kwboot_path, self.uart_uboot_path, self.tty_path
            ))

            while True:
                plan = [
                    (pexpect.EOF, 90),
                    (pexpect.TIMEOUT, 0),
                    ('20 %', 15),
                    ('40 %', 35),
                    ('60 %', 55),
                    ('80 %', 75),
                ]
                res = self.expect(exp, [e[0] for e in plan], timeout=30)

                if res == 1:  # timeout exit with an error
                    exp.terminate(force=True)
                    return False

                self.progress.emit(plan[res][1])

                if res == 0:  # first is a final success
                    break
                else:
                    # remove from plan (avoid going in boot cyrcles)
                    del plan[res]

            self.testExitStatus(exp)
            self.progress.emit(100)

            return True


class RewriteUboot(Base):
    _name = "UBOOT REWRITE"

    def __init__(self, eth):
        self.eth = eth

    def createWorker(self):
        return self.Worker(
            settings.PATHS['uboot_reflash']['write_script'],
            self.eth,
            settings.REFLASH['server_ip'],
            settings.REFLASH['router_ip'],
            settings.PATHS['uboot_reflash']['img_file'],
            settings.PATHS['uboot_reflash']['tty'],
        )

    class Worker(BaseWorker):
        def __init__(self, write_script_path, eth, server_ip, router_ip, img_file_path, tty_path):
            super(RewriteUboot.Worker, self).__init__()
            self.write_script_path = write_script_path
            self.eth = eth
            self.server_ip = server_ip
            self.router_ip = router_ip
            self.img_file_path = img_file_path
            self.img_file = os.path.basename(img_file_path)
            self.tty_path = tty_path

        def perform(self):
            self.progress.emit(1)

            # setup network
            self.expectLocalCommand("sudo ip address flush dev %s" % self.eth)
            self.progress.emit(5)

            self.expectLocalCommand(
                "sudo ip address add %s/24 dev %s" % (self.server_ip, self.eth)
            )
            self.progress.emit(10)

            self.expectLocalCommand("sudo ip link set dev %s up" % self.eth)
            self.progress.emit(15)

            # run command
            exp = self.expectStartLocalCommand("%s %s %s %s %s" % (
                self.write_script_path, self.server_ip, self.router_ip, self.img_file,
                self.tty_path
            ))

            while True:
                plan = [
                    (pexpect.EOF, 90),
                    (pexpect.TIMEOUT, 0),
                    ('Loading: ', 20),
                    ('Bytes transferred', 40),
                    ('Erased: OK', 55),
                    ('Written: OK', 70),
                ]
                res = self.expect(exp, [e[0] for e in plan], timeout=60)

                if res == 1:  # timeout exit with an error
                    exp.terminate(force=True)
                    return False

                self.progress.emit(plan[res][1])

                if res == 0:  # first is a final success
                    break
                else:
                    # remove from plan (avoid going in boot cyrcles)
                    del plan[res]

            self.testExitStatus(exp)
            self.progress.emit(80)

            # store the result
            self.uboot.emit(md5File(self.img_file_path))
            self.progress.emit(85)

            # local cleanup
            self.expectLocalCommand("sudo ip link set dev %s down" % self.eth)
            self.progress.emit(90)
            self.expectLocalCommand("sudo ip address flush dev %s" % self.eth)
            self.progress.emit(100)

            return True

TESTS = (
    Beacon(),
    LoadUboot(),
    RewriteUboot('ethTEST'),
)
