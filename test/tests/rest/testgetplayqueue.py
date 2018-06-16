import xml.etree.ElementTree as ET

from unsonic.views.rest.getplayqueue import GetPlayQueue
from unsonic.views.rest.saveplayqueue import SavePlayQueue
from . import buildCmd, checkResp


def testGetPlayQueue(session):
    cmd = buildCmd(session, SavePlayQueue,
                   {"id": "tr-1", "id": "tr-2", "id": "tr-3",
                    "current": "tr-2", "position": "32000"})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, GetPlayQueue, {})
    resp = checkResp(cmd.req, cmd())
    pq = resp.find("{http://subsonic.org/restapi}playQueue")
    assert pq != None
    assert pq.get("changed")
    assert pq.get("changedBy") == cmd.req.user_agent
    assert pq.get("current") == "tr-2"
    assert pq.get("position") == "32000"
    assert pq.get("username") == "test"
    for entry in pq.iter("{http://subsonic.org/restapi}entry"):
        assert entry.get("album")
        assert entry.get("artist")
        assert entry.get("bitRate")
        assert entry.get("contentType")
        assert entry.get("coverArt")
        assert entry.get("discNumber")
        assert entry.get("duration")
        assert entry.get("genre")
        assert entry.get("isDir")
        assert entry.get("isVideo")
