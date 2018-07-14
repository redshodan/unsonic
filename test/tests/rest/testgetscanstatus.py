from unsonic.views.rest.getscanstatus import GetScanStatus
from . import buildCmd, checkResp


def testGetScanStatus(session):
    cmd = buildCmd(session, GetScanStatus, {})
    resp = checkResp(cmd.req, cmd())
    scanstatus = resp.find("{http://subsonic.org/restapi}scanStatus")
    assert scanstatus.get("scanning") == "false"
    assert scanstatus.get("count") is not None
