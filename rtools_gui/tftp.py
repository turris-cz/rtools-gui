import os
import tempfile


# Note that tempfile.NamedTemporaryFile is actually a function
# so we use Camel case here to express that TFTPFile is derived from that
def TFTPFile(dir: str, content: bytes):
    """Helper to provide files trough TFTP server.
    """
    res = tempfile.NamedTemporaryFile(mode="w+b", dir=dir)
    res.file.write(content)
    res.file.seek(0)

    # change file mask so that tftp user can read it
    os.fchmod(res.file.fileno(), 0o0444)

    return res
