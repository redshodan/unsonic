import pytest

from unsonic.views.rest.getalbumlist import GetAlbumList
from unsonic.views.rest.getalbumlist2 import GetAlbumList2
from unsonic.views.rest import Command
from . import buildCmd, checkResp


@pytest.fixture(scope="function", params=[GetAlbumList, GetAlbumList2])
def album_list(request):
    yield request.param


def validate(cmd, resp, al_class):
    if al_class == GetAlbumList:
        al_name = "albumList"
    else:
        al_name = "albumList2"
    sub_resp = checkResp(cmd.req, resp)
    alist = sub_resp.find("{http://subsonic.org/restapi}" + al_name)
    count = 0
    titles = []
    for album in alist.iter("{http://subsonic.org/restapi}album"):
        count += 1
        titles.append(album.get("title"))
        assert album.get("id").startswith("al-")
        if al_class == GetAlbumList:
            assert len(album.get("title")) > 0
            assert album.get("isDir") == "true"
        else:
            assert len(album.get("name")) > 0
    return count, titles


def testRandom(session, album_list):
    cmd = buildCmd(session, album_list, {"type": "random"})
    resp = cmd()
    count1, titles1 = validate(cmd, resp, album_list)


def testSized(session, album_list):
    cmd = buildCmd(session, album_list, {"type": "random", "size": "2"})
    resp = cmd()
    count, titles = validate(cmd, resp, album_list)
    assert count == 2


def testOffset(session, album_list):
    cmd = buildCmd(session, album_list, {"type": "random", "size": "3",
                                         "offset": "1"})
    resp = cmd()
    count, titles = validate(cmd, resp, album_list)
    assert count == 4


def testOffset2(session, album_list):
    cmd = buildCmd(session, album_list, {"type": "random", "size": "3",
                                         "offset": "2"})
    resp = cmd()
    count, titles = validate(cmd, resp, album_list)
    assert count == 5


def testNewest(session, album_list):
    cmd = buildCmd(session, album_list, {"type": "newest"})
    resp = cmd()
    count1, titles1 = validate(cmd, resp, album_list)

    cmd = buildCmd(session, album_list, {"type": "newest"})
    resp = cmd()
    count2, titles2 = validate(cmd, resp, album_list)

    assert titles1 == titles2


def testNoType(session, album_list):
    cmd = buildCmd(session, album_list)
    resp = cmd()
    checkResp(cmd.req, resp, Command.E_MISSING_PARAM)


def testByGenre(session, album_list):
    cmd = buildCmd(session, album_list, {
                   "type": "byGenre", "genre": "techno"})
    resp = cmd()
    count1, titles1 = validate(cmd, resp, album_list)


def testByGenreNoGenre(session, album_list):
    cmd = buildCmd(session, album_list, {"type": "byGenre"})
    resp = cmd()
    checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
