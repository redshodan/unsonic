from unsonic.views.rest.getgenres import GetGenres
from . import buildCmd, checkResp


def testGetGenres(session):
    cmd = buildCmd(session, GetGenres, {})
    resp = checkResp(cmd.req, cmd())
    genres = resp.find("{http://subsonic.org/restapi}genres")
    assert genres
    for genre in genres.iter("{http://subsonic.org/restapi}genre"):
        assert genre.get("albumCount")
        assert genre.get("songCount")
