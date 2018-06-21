from unsonic.models import PlayList
from unsonic.views.rest.createplaylist import CreatePlayList
from unsonic.views.rest.updateplaylist import UpdatePlayList
from . import buildCmd, checkResp


def testUpdatePlayList(session):
    pname = "playlist1"
    plist = ["tr-1", "tr-2", "tr-3"]
    cmd = buildCmd(session, CreatePlayList, {"name": pname, "songId": plist})
    sub_resp = checkResp(cmd.req, cmd())
    playlist = sub_resp.find("{http://subsonic.org/restapi}playlist")
    pl_id = playlist.get("id")

    plist2 = ["tr-4"]
    cmd = buildCmd(session, UpdatePlayList,
                   {"playlistId": pl_id, "songIdToAdd": plist2})
    checkResp(cmd.req, cmd())
    row = session.query(PlayList).\
        filter(PlayList.name == pname).one_or_none()
    assert row is not None
    assert ([t.track_id for t in row.tracks] ==
            [int(t.replace("tr-", "")) for t in plist + plist2])
    assert row.owner.name == "test"
