import time

from unsonic.views.rest.scrobble import Scrobble
from . import buildCmd, checkResp


def testScrobble(session):
    cmd = buildCmd(session, Scrobble, {"id": "tr-1"})
    checkResp(cmd.req, cmd())


def testScrobbleSubmission(session):
    cmd = buildCmd(session, Scrobble,
                   {"id": "tr-1", "time": str(int(time.time()) * 1000),
                    "submission":"True"})
    checkResp(cmd.req, cmd())


def testScrobbleSubmissionNoTime(session):
    cmd = buildCmd(session, Scrobble, {"id": "tr-1", "submission":"True"})
    checkResp(cmd.req, cmd())
