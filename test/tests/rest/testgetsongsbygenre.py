from unsonic.views.rest.getsongsbygenre import GetSongsByGenre
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testGetSongsByGenre(session):
    cmd = buildCmd(session, GetSongsByGenre, {"genre": "rock"})
    resp = checkResp(cmd.req, cmd())
    songs = resp.find("{http://subsonic.org/restapi}songsByGenre")
    for song in songs.iter("{http://subsonic.org/restapi}song"):
        assert song.get("id").startswith("tr-")
