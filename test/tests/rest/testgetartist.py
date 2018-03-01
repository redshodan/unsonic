from unsonic.views.rest.getartist import GetArtist
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testNoAlbums(session):
    aid = "ar-1"
    cmd = buildCmd(session, GetArtist, {"id": aid})
    sub_resp = checkResp(cmd.req, cmd())
    artist = sub_resp.find("{http://subsonic.org/restapi}artist")
    assert artist.get("id") == aid


def testTwoAlbums(session):
    aid = "ar-2"
    cmd = buildCmd(session, GetArtist, {"id": aid})
    sub_resp = checkResp(cmd.req, cmd())
    artist = sub_resp.find("{http://subsonic.org/restapi}artist")
    assert artist.get("id") == aid
    for album in artist.iter("{http://subsonic.org/restapi}album"):
        assert album.get("id").startswith("al-")
        assert int(album.get("id")[3:]) > 0
        assert album.get("artist") == artist.get("name")
        assert int(album.get("songCount")) > 0
        assert int(album.get("duration")) >= 0


def testNotFound(session):
    cmd = buildCmd(session, GetArtist, {"id": "ar-1000000000000"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)


def testBadID(session):
    cmd = buildCmd(session, GetArtist, {"id": "foobar"})
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)


def testNoID(session):
    cmd = buildCmd(session, GetArtist)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
