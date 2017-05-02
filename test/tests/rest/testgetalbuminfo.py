from unsonic.views.rest.getalbuminfo import GetAlbumInfo
from . import buildCmd, checkResp


def testGetAlbumInfo(session, ptesting):
    cmd = buildCmd(session, GetAlbumInfo, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
