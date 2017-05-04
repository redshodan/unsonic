import time
import threading
from multiprocessing import Process
from sqlalchemy import func

from . import __main__, web
from .log import log
from .models import Track


sync_proc = None
last_sync_ret = None
check_thread = None


def doSync():
    log.info("Starting music sync...")
    __main__.main(["-c", web.CONFIG_FILE, "sync"])
    return True


def startSync(session):
    global sync_proc
    log.info("Starting music sync subprocess...")
    startChecker()
    sync_proc = Process(target=doSync, name="Sync Task")
    sync_proc.start()
    return syncStatus(session)


def syncStatus(session):
    count = session.query(func.count(Track.id)).one()[0]
    if sync_proc and sync_proc.is_alive():
        return (True, count)
    else:
        return (False, count)


def startChecker():
    global check_thread
    if check_thread:
        return
    check_thread = threading.Thread(target=checkProc, name="Sync proc checker")
    check_thread.daemon = True
    check_thread.start()


def checkProc():
    global sync_proc
    while True:
        time.sleep(5.0)
        if sync_proc and not sync_proc.is_alive():
            log.debug("Joining sync proccess...")
            sync_proc.join()
            log.debug("Joined sync proccess")
            sync_proc = None
