from unsonic.models import Share
from unsonic.views.rest.createshare import CreateShare
from unsonic.views.rest.updateshare import UpdateShare
from . import buildCmd, checkResp


def testUpdateShare(session):
    desc = "share1 description"
    slist = ["tr-1", "al-2", "tr-3"]
    cmd = buildCmd(session, CreateShare, {"description": desc, "id": slist})
    sub_resp = checkResp(cmd.req, cmd())

    shares = sub_resp.find("{http://subsonic.org/restapi}shares")
    share = shares.find("{http://subsonic.org/restapi}share")
    sid = share.get("id")

    ndesc = "new share1 description"
    cmd = buildCmd(session, UpdateShare, {"description": ndesc, "id": sid})
    checkResp(cmd.req, cmd())

    row = session.query(Share).filter(Share.description == ndesc).one_or_none()
    assert row is not None
