from webob.multidict import MultiDict

from unsonic.views.rest.saveplayqueue import SavePlayQueue
from . import buildCmd, checkResp


def testSavePlayQueue(session):
    md = MultiDict()
    md.add("id", "tr-1")
    md.add("id", "tr-2")
    md.add("id", "tr-3")
    md.add("current", "tr-2")
    md.add("position", "32000")
    cmd = buildCmd(session, SavePlayQueue, md)
    checkResp(cmd.req, cmd())
