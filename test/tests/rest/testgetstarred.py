from unsonic.views.rest.star import Star
from unsonic.views.rest.getstarred import GetStarred
from . import buildCmd, checkResp


def testGetStarred(session):
    cmd = buildCmd(session, Star, {"id": "tr-1"})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, GetStarred, {})
    resp = checkResp(cmd.req, cmd())
    starred = resp.find("{http://subsonic.org/restapi}starred")
    assert len(starred.getchildren()) == 2
    album = starred.find("{http://subsonic.org/restapi}album")
    assert album.get("id") == "al-1"
    song = starred.find("{http://subsonic.org/restapi}song")
    assert song.get("id") == "tr-1"


def testGetStarredEmpty(session):
    cmd = buildCmd(session, GetStarred, {})
    resp = checkResp(cmd.req, cmd())
    starred = resp.find("{http://subsonic.org/restapi}starred")
    assert len(starred.getchildren()) == 0
