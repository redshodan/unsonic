from unsonic.views.rest.getnowplaying import GetNowPlaying
from . import buildCmd, checkResp


def testGetPlayList(session):
    cmd = buildCmd(session, GetNowPlaying, {})
    checkResp(cmd.req, cmd())
