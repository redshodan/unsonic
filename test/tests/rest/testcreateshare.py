from unsonic.models import Share
from unsonic.views.rest.createshare import CreateShare
from . import buildCmd, checkResp


def testCreateShare(session):
    desc = "share1 description"
    slist = ["tr-1", "al-2", "tr-3"]
    cmd = buildCmd(session, CreateShare, {"description": desc, "id": slist})
    checkResp(cmd.req, cmd())
    row = session.query(Share).filter(Share.description == desc).one_or_none()
    assert row is not None
    assert row.entries[0].track_id == 1
    assert row.entries[1].album_id == 2
    assert row.entries[2].track_id == 3
    assert row.user.name == "test"
