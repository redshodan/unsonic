from unsonic.views.rest.hls import HLS
from unsonic.views.rest import Command
from . import buildCmd, checkResp


# Empty command, since not implemented
def testHLS(session):
    cmd = buildCmd(session, HLS, {"id": "tr-1"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)
