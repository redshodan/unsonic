from unsonic.models import PlayList
from unsonic.views.rest.createplaylist import CreatePlayList
from unsonic.views.rest.deleteplaylist import DeletePlayList
from . import buildCmd, checkResp


def testDeletePlayList(session, ptesting):
    pname = "playlist1"
    plist = ["tr-1", "tr-2", "tr-3"]
    cmd = buildCmd(session, CreatePlayList, {"name": pname, "songId": plist})
    resp = cmd()
    sub_resp = checkResp(cmd.req, resp)

    row = session.query(PlayList).\
              filter(PlayList.name == pname).one_or_none()
    assert row is not None

    pl = sub_resp.find("{http://subsonic.org/restapi}playlist")
    plid = pl.get("id")
    cmd = buildCmd(session, DeletePlayList, {"id": plid})
    checkResp(cmd.req, cmd())

    row = session.query(PlayList).\
              filter(PlayList.name == pname).one_or_none()
    assert row is None
