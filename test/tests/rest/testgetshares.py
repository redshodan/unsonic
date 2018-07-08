from unsonic.models import Share
from unsonic.views.rest.createshare import CreateShare
from unsonic.views.rest.getshares import GetShares
from . import buildCmd, checkResp


def testCreateShare(session):
    desc = "share1 description"
    slist = ["tr-1", "al-2", "tr-3"]
    cmd = buildCmd(session, CreateShare, {"description": desc, "id": slist})
    sub_resp = checkResp(cmd.req, cmd())
    row = session.query(Share).filter(Share.description == desc).one_or_none()
    assert row is not None

    shares = sub_resp.find("{http://subsonic.org/restapi}shares")
    share = shares.find("{http://subsonic.org/restapi}share")
    sid = share.get("id")

    cmd = buildCmd(session, GetShares, {"id": sid})
    checkResp(cmd.req, cmd())
