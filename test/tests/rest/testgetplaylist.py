from unsonic.views.rest.getplaylist import GetPlayList
from unsonic.views.rest.createplaylist import CreatePlayList
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testGetPlayList(session):
    pname = "playlist1"
    plist = ["tr-1", "tr-2", "tr-3"]
    cmd = buildCmd(session, CreatePlayList, {"name": pname, "songId": plist})
    sub_resp = checkResp(cmd.req, cmd())
    playlist = sub_resp.find("{http://subsonic.org/restapi}playlist")
    pl_id = playlist.get("id")

    cmd = buildCmd(session, GetPlayList, {"id": pl_id})
    resp = checkResp(cmd.req, cmd())
    pl = resp.find("{http://subsonic.org/restapi}playlist")
    assert pl
    for entry in pl.iter("{http://subsonic.org/restapi}entry"):
        assert entry.get("album")
        assert entry.get("artist")
        assert entry.get("bitRate")
        assert entry.get("contentType")
        assert entry.get("discNumber")
        assert entry.get("id")
        assert entry.get("isDir")
        assert entry.get("isVideo")
        assert entry.get("parent")
        assert entry.get("path")
        assert entry.get("size")
        assert entry.get("suffix")
        assert entry.get("title")
        assert entry.get("transcodedContentType")
        assert entry.get("transcodedSuffix")
        assert entry.get("year")


def testGetPlayListEmpty(session):
    cmd = buildCmd(session, GetPlayList, {"id": "pl-1"})
    checkResp(cmd.req, cmd(), ok=Command.E_NOT_FOUND)
