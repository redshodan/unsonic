from unsonic.views.rest.scrobble import Scrobble
from . import buildCmd, checkResp


def testScrobble(session):
    cmd = buildCmd(session, Scrobble, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
