from PyQt5.QtCore import QSharedMemory, QSystemSemaphore


class GuardFailed(Exception):
    def __init__(self, *args, **kwargs):
        super(GuardFailed, self).__init__("Another program instance is running.")


class Guard(object):

    def __init__(self, part=""):
        self.part = part

    def __enter__(self):
        mem_key = "rtools_gui_%s_shmem" % self.part if self.part else "rtools_gui_shmem"
        sem_key = "rtools_gui_%s_lock" % self.part if self.part else "rtools_gui_lock"
        self.status = QSharedMemory(mem_key)
        self.lock = QSystemSemaphore(sem_key, 1, QSystemSemaphore.Open)

        if not self.lock.acquire():
            raise GuardFailed()

        # cleanup after crashed process
        QSharedMemory(mem_key).attach()

        if not self.status.create(1):
            self.lock.release()
            raise GuardFailed()

        if not self.lock.release():
            raise GuardFailed()

    def __exit__(self, *args, **kwargs):
        self.lock.acquire()
        self.status.detach()
        self.lock.release()
