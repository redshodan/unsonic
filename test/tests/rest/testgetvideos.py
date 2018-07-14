from unsonic.views.rest.getvideos import GetVideos
from . import buildCmd, checkResp


# Empty command, since not implemented
def testGetVideos(session):
    cmd = buildCmd(session, GetVideos, {})
    checkResp(cmd.req, cmd())
