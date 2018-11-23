import os
import errno
import fcntl


class GuardFailed(Exception):
    def __init__(self, *args, **kwargs):
        super(GuardFailed, self).__init__(
            "Another program instance is running.")


class Guard(object):

    def __init__(self, conf):
        self.path = os.path.join(conf.tmp_dir, 'rtools-gui.lock')
        self.file = None

    def __enter__(self):
        self.file = os.open(self.path, os.O_WRONLY | os.O_SYNC | os.O_CREAT)
        try:
            fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as excp:
            if excp.errno == errno.EWOULDBLOCK:
                raise GuardFailed()
            raise

    def __exit__(self, *args, **kwargs):
        os.remove(self.path)
        os.close(self.file)
