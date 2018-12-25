from webob.multidict import MultiDict

from unsonic.views.rest.getplayqueue import GetPlayQueue
from unsonic.views.rest.saveplayqueue import SavePlayQueue
from . import buildCmd, checkResp


def testGetPlayQueue(session):
    md = MultiDict()
    md.add("id", "tr-1")
    md.add("id", "tr-2")
    md.add("id", "tr-3")
    md.add("current", "tr-2")
    md.add("position", "32000")
    cmd = buildCmd(session, SavePlayQueue, md)
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, GetPlayQueue, {})
    resp = checkResp(cmd.req, cmd())
    pq = resp.find("{http://subsonic.org/restapi}playQueue")
    assert pq is not None
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
        assert entry.get("discNumber")
        assert entry.get("duration")
        assert entry.get("isDir")
        assert entry.get("isVideo")
