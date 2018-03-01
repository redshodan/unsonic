from unsonic.views.rest.getartistinfo import GetArtistInfo
from . import buildCmd, checkResp


def testGetArtistInfo(session):
    cmd = buildCmd(session, GetArtistInfo, {"id": "ar-1"})
    checkResp(cmd.req, cmd())
