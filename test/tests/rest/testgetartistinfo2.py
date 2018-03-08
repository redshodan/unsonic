from unsonic.views.rest.getartistinfo2 import GetArtistInfo2
from . import buildCmd, checkResp


def testGetArtistInfo2(session):
    cmd = buildCmd(session, GetArtistInfo2, {"id": "ar-1"})
    checkResp(cmd.req, cmd())
