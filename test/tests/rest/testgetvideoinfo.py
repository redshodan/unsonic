from unsonic.views.rest.getvideoinfo import GetVideoInfo
from unsonic.views.rest import Command
from . import buildCmd, checkResp


# Empty command, since not implemented
def testGetVideoInfo(session):
    cmd = buildCmd(session, GetVideoInfo, {"id": "foo"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)
