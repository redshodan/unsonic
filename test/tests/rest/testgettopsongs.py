from unsonic.views.rest.gettopsongs import GetTopSongs
from . import buildCmd, checkResp


# Mildly iffy, relying on last.fm returning this song always
def testGetTopSongs(session):
    cmd = buildCmd(session, GetTopSongs, {"artist": "Daft Punk"})
    resp = checkResp(cmd.req, cmd(), ok504=True)
    if resp is False:
        return
    top = resp.find("{http://subsonic.org/restapi}topSongs")
    song = top.find("{http://subsonic.org/restapi}song")
    assert song.get("title") == "Harder, Better, Faster, Stronger"
