from unsonic.views.rest.getsimilarsongs import GetSimilarSongs
from . import buildCmd, checkResp


def testGetSimilarSongs(session):
    cmd = buildCmd(session, GetSimilarSongs, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
