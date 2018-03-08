from unsonic.views.rest.getalbumlist import GetAlbumList
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def validate(cmd, resp):
    sub_resp = checkResp(cmd.req, resp)
    alist = sub_resp.find("{http://subsonic.org/restapi}albumList")
    count = 0
    titles = []
    for album in alist.iter("{http://subsonic.org/restapi}album"):
        count += 1
        titles.append(album.get("title"))
        assert album.get("id").startswith("al-")
        assert len(album.get("title")) > 0
        assert album.get("isDir") == "true"
    return count, titles


def testRandom(session):
    cmd = buildCmd(session, GetAlbumList, {"type": "random"})
    resp = cmd()
    count1, titles1 = validate(cmd, resp)


def testSized(session):
    cmd = buildCmd(session, GetAlbumList, {"type": "random", "size": "2"})
    resp = cmd()
    count, titles = validate(cmd, resp)
    assert count == 2


def testOffset(session):
    cmd = buildCmd(session, GetAlbumList, {"type": "random", "size": "3",
                                           "offset": "1"})
    resp = cmd()
    count, titles = validate(cmd, resp)
    assert count == 4


def testOffset2(session):
    cmd = buildCmd(session, GetAlbumList, {"type": "random", "size": "3",
                                           "offset": "2"})
    resp = cmd()
    count, titles = validate(cmd, resp)
    assert count == 5


def testNewest(session):
    cmd = buildCmd(session, GetAlbumList, {"type": "newest"})
    resp = cmd()
    count1, titles1 = validate(cmd, resp)

    cmd = buildCmd(session, GetAlbumList, {"type": "newest"})
    resp = cmd()
    count2, titles2 = validate(cmd, resp)

    assert titles1 == titles2


def testNoType(session):
    cmd = buildCmd(session, GetAlbumList)
    resp = cmd()
    checkResp(cmd.req, resp, Command.E_MISSING_PARAM)


def testByGenre(session):
    cmd = buildCmd(session, GetAlbumList, {
                   "type": "byGenre", "genre": "techno"})
    resp = cmd()
    count1, titles1 = validate(cmd, resp)


def testByGenreNoGenre(session):
    cmd = buildCmd(session, GetAlbumList, {"type": "byGenre"})
    resp = cmd()
    checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
