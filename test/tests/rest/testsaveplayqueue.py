from unsonic.views.rest.saveplayqueue import SavePlayQueue
from . import buildCmd, checkResp


def testSavePlayQueue(session):
    cmd = buildCmd(session, SavePlayQueue,
                   {"id": "tr-1", "id": "tr-2", "id": "tr-3",
                    "current": "tr-2", "position": "32000"})
    checkResp(cmd.req, cmd())
