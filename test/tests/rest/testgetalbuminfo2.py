from unsonic.views.rest.getalbuminfo2 import GetAlbumInfo2
from . import buildCmd, checkResp


def testGetAlbumInfo(session):
    cmd = buildCmd(session, GetAlbumInfo2, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
