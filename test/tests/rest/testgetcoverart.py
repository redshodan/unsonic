from unsonic.views.rest.getcoverart import GetCoverArt
from unsonic.views.rest import Command
from unsonic.models import Artist, Album
from . import buildCmd, checkResp
from unsonic.config import CONFIG


def testBasic(session):
    # Don't hit lastfm for a picture for this test
    CONFIG.setDbValue(session, "art.never_lastfm", True)
    artist = session.query(Artist).\
             filter(Artist.name == "artist 1").one_or_none()
    album = session.query(Album).\
            filter(Album.title == "album 1",
                   Album.artist_id == artist.id).one_or_none()
    image = album.images[0]
    cmd = buildCmd(session, GetCoverArt, {"id": "al-%d" % album.id})
    resp = cmd()
    assert len(resp.body) == len(image.data)
    assert resp.body == image.data


def testNoID(session):
    cmd = buildCmd(session, GetCoverArt)
    checkResp(cmd.req, cmd(), Command.E_MISSING_PARAM)
