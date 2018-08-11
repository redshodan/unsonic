from unsonic.views.rest.getlyrics import GetLyrics
from . import buildCmd, checkResp


def testGetLyrics(session):
    cmd = buildCmd(session, GetLyrics, {"artist": "Tool", "title": "Stinkfist"})
    checkResp(cmd.req, cmd(), ok504=True)


def testGetLyricsByID(session):
    cmd = buildCmd(session, GetLyrics, {"id": "tr-1"})
    checkResp(cmd.req, cmd(), ok504=True)
