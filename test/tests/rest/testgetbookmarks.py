from unsonic.models import dbinfo, Bookmark
from unsonic.views.rest.createbookmark import CreateBookmark
from unsonic.views.rest.getbookmarks import GetBookmarks
from . import buildCmd, checkResp


def testGetBookmarks(session):
    id = 1
    tr_id = "tr-%d" % id
    position = 49201
    comment = "comment1"

    cmd = buildCmd(session, CreateBookmark,
                   {"id": tr_id, "position": str(position), "comment": comment})
    checkResp(cmd.req, cmd())
    row = session.query(Bookmark).\
        filter(Bookmark.user_id == dbinfo.users["test"].id,
               Bookmark.track_id == id).one_or_none()
    assert row is not None
    assert row.user.name == "test"

    cmd = buildCmd(session, GetBookmarks, {})
    sub_resp = checkResp(cmd.req, cmd())
    bms = sub_resp.find("{http://subsonic.org/restapi}bookmarks")
    bm = bms.find("{http://subsonic.org/restapi}bookmark")
    entry = bm.find("{http://subsonic.org/restapi}entry")
    assert bm.get("comment") == comment
    assert bm.get("position") == str(position)
    assert bm.get("created") is not None
    assert bm.get("changed") is not None
    assert entry.get("id") == tr_id
