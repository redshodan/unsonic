from unsonic import sync
from unsonic.views.rest.startscan import StartScan
from unsonic.views.rest.getscanstatus import GetScanStatus
from . import buildCmd, checkResp


def testStartScan(session):
    cmd = buildCmd(session, StartScan, {})
    resp = checkResp(cmd.req, cmd())
    scanstatus = resp.find("{http://subsonic.org/restapi}scanStatus")
    assert scanstatus.get("scanning") == "true"
    assert scanstatus.get("count") != None

    # Wait for the scan proc to finish
    while True:
        cmd = buildCmd(session, GetScanStatus, {})
        resp = checkResp(cmd.req, cmd())
        scanstatus = resp.find("{http://subsonic.org/restapi}scanStatus")
        if scanstatus.get("scanning") == "false":
            break
