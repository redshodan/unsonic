from unsonic.views.rest.getalbum import GetAlbum
from . import buildCmd, checkResp


def testGetAlbum(session):
    alid = "al-1"
    cmd = buildCmd(session, GetAlbum, {"id": alid})
    sub_resp = checkResp(cmd.req, cmd())
    album = sub_resp.find("{http://subsonic.org/restapi}album")
    assert album.get("id") == alid
    assert len(album.get("name")) > 0
