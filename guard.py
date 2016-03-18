from PyQt5.QtCore import QSharedMemory, QSystemSemaphore

class GuardFailed(Exception):
    def __init__(self, *args, **kwargs):
        super(GuardFailed, self).__init__("Another program instance is running.")

class Guard(object):

    def __enter__(self):
        self.status = QSharedMemory("rtools_gui_shmem")
        self.lock = QSystemSemaphore("rtools_gui_lock", 1, QSystemSemaphore.Open)

        if not self.lock.acquire():
            raise GuardFailed()

        # cleanup after crashed process
        QSharedMemory("rtools_gui_shmem").attach()

        if not self.status.create(1):
            self.lock.release()
            raise GuardFailed()

        if not self.lock.release():
            raise GuardFailed()

    def __exit__(self, *args, **kwargs):
        self.lock.acquire()
        self.status.detach()
        self.lock.release()
