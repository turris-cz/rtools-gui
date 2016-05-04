import math

MAX_SERIAL = (2 ** 64 - 1)
MAX_SERIAL_LEN = math.ceil(math.log10(MAX_SERIAL))


def serialNumberValidator(sn):
    # serial number must be integer
    try:
        sn = int(sn)
    except ValueError:
        return False

    # it cannot be negative
    if sn < 0:
        return False

    # it cannot be bigger than MAX_SERIAL
    if sn > MAX_SERIAL:
        return False

    # it must be divisible by 11 or 503316xx (test serie)
    if sn % 11 != 0 and sn / 100 != 503316:
        return False

    return True


def backupFile(path):
    from application import settings, qApp
    from PyQt5.QtCore import QProcess
    # start detached process
    res, pid = QProcess.startDetached(settings.BACKUP_SCRIPT, [path], None)
    if res:
        qApp.loggerMain.info(
            "Backup process started. '%s %s' (pid %d)" % (
                settings.BACKUP_SCRIPT, path, pid
            )
        )
    else:
        qApp.loggerMain.error(
            "Failed to start backup process! '%s %s'" % (
                settings.BACKUP_SCRIPT, path
            )
        )


def backupAppLog():
    from application import settings
    backupFile(settings.LOG_APP_FILE)
