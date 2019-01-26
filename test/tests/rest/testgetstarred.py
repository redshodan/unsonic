import pytest

from unsonic.views.rest import fillID
from unsonic.views.rest.star import Star
from unsonic.views.rest.getstarred import GetStarred
from unsonic.views.rest.getstarred2 import GetStarred2
from . import buildCmd, checkResp, getRows


@pytest.fixture(scope="function", params=[(GetStarred, "starred"),
                                          (GetStarred2, "starred2")])
def starred(request):
    yield request.param



def testGetStarred(session, starred):
    ar, al, tr = getRows(session, "artist 1", "album 1", "song 1")

    cmd = buildCmd(session, Star, {"id": fillID(tr[0])})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, starred[0], {})
    resp = checkResp(cmd.req, cmd())
    starred = resp.find("{http://subsonic.org/restapi}" + starred[1])
    assert len(starred.getchildren()) == 2
    album = starred.find("{http://subsonic.org/restapi}album")
    assert album.get("id") == fillID(al[0])
    song = starred.find("{http://subsonic.org/restapi}song")
    assert song.get("id") == fillID(tr[0])


def testGetStarredEmpty(session, starred):
    cmd = buildCmd(session, starred[0], {})
    resp = checkResp(cmd.req, cmd())
    starred = resp.find("{http://subsonic.org/restapi}" + starred[1])
    assert len(starred.getchildren()) == 0
