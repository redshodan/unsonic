from unsonic.models import dbinfo, Bookmark
from unsonic.views.rest.createbookmark import CreateBookmark
from . import buildCmd, checkResp


def testCreateBookmark(session):
    id = 1
    position = 49201
    comment = "comment1"

    cmd = buildCmd(session, CreateBookmark,
                   {"id": "tr-%d" % id, "position": position, "comment": comment})
    checkResp(cmd.req, cmd())
    row = session.query(Bookmark).\
        filter(Bookmark.user_id == dbinfo.users["test"].id,
               Bookmark.track_id == id).one_or_none()
    assert row is not None
    assert row.user.name == "test"
