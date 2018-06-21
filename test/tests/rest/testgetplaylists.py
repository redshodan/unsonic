import xml.etree.ElementTree as ET

from unsonic.models import PlayList
from unsonic.views.rest.getplaylists import GetPlayLists
from unsonic.views.rest.createplaylist import CreatePlayList
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testGetPlayLists(session):
    pname = "playlist1"
    plist = ["tr-1", "tr-2", "tr-3"]
    cmd = buildCmd(session, CreatePlayList, {"name": pname, "songId": plist})
    sub_resp = checkResp(cmd.req, cmd())
    playlist = sub_resp.find("{http://subsonic.org/restapi}playlist")
    pl_id = playlist.get("id")

    cmd = buildCmd(session, GetPlayLists, {})
    resp = checkResp(cmd.req, cmd())
    pls = resp.find("{http://subsonic.org/restapi}playlists")
    assert pls != None
    for pl in pls.iter("{http://subsonic.org/restapi}playlist"):
        assert pl.get("changed")
        assert pl.get("created")
        assert pl.get("duration")
        assert pl.get("id")
        assert pl.get("owner")
        assert pl.get("public")
        assert pl.get("songCount")


def testGetPlayListsEmpty(session):
    cmd = buildCmd(session, GetPlayLists, {"id": "pl-1"})
    resp = checkResp(cmd.req, cmd())
    pls = resp.find("{http://subsonic.org/restapi}playlists")
    assert pls != None
    assert pls.find("{http://subsonic.org/restapi}playlist") == None
