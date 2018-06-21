from unsonic.views.rest.getsong import GetSong
from . import buildCmd, checkResp


def testGetSong(session):
    cmd = buildCmd(session, GetSong, {"id": "tr-1"})
    resp = checkResp(cmd.req, cmd())
    song = resp.find("{http://subsonic.org/restapi}song")
    assert song.get("id").startswith("tr-")
