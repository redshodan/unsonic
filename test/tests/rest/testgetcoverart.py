from unsonic.views.rest.getcoverart import GetCoverArt
from unsonic.views.rest import Command
from unsonic.models import Artist, Album
from . import buildCmd, checkResp
from unsonic.config import CONFIG


def testGetByArtist(session):
    # Don't hit lastfm for a picture for this test
    CONFIG.setDbValue(session, "art.never_lastfm", True)
    artist = session.query(Artist).\
             filter(Artist.name == "artist 1").one_or_none()
    image = artist.images[0]
    cmd = buildCmd(session, GetCoverArt, {"id": "ca-ar-%d" % artist.id})
    resp = cmd()
    assert len(resp.body) == len(image.data)
    assert resp.body == image.data


def testGetByAlbum(session):
    # Don't hit lastfm for a picture for this test
    CONFIG.setDbValue(session, "art.never_lastfm", True)
    artist = session.query(Artist).\
             filter(Artist.name == "artist 1").one_or_none()
    album = session.query(Album).\
            filter(Album.title == "album 1",
                   Album.artist_id == artist.id).one_or_none()
    image = album.images[0]
    cmd = buildCmd(session, GetCoverArt, {"id": "ca-al-%d" % album.id})
    resp = cmd()
    assert len(resp.body) == len(image.data)
    assert resp.body == image.data


def testGetByTrack(session):
    # Don't hit lastfm for a picture for this test
    CONFIG.setDbValue(session, "art.never_lastfm", True)
    artist = session.query(Artist).\
             filter(Artist.name == "artist 1").one_or_none()
    album = session.query(Album).\
            filter(Album.title == "album 1",
                   Album.artist_id == artist.id).one_or_none()
    track = album.tracks[0]
    image = album.images[0]
    cmd = buildCmd(session, GetCoverArt, {"id": "ca-tr-%d" % track.id})
    resp = cmd()
    assert len(resp.body) == len(image.data)
    assert resp.body == image.data


def testGetBadID(session):
    # Don't hit lastfm for a picture for this test
    CONFIG.setDbValue(session, "art.never_lastfm", True)
    cmd = buildCmd(session, GetCoverArt, {"id": "ca-ar-60000"})
    checkResp(cmd.req, cmd(), Command.E_NOT_FOUND)


def testNoID(session):
    cmd = buildCmd(session, GetCoverArt)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
