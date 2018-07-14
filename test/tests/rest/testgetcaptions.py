from unsonic.views.rest.getcaptions import GetCaptions
from unsonic.views.rest import Command
from . import buildCmd, checkResp


# Empty command, since not implemented
def testGetCaptions(session):
    cmd = buildCmd(session, GetCaptions, {"id": "foo"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)
