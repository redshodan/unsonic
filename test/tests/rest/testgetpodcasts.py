from unsonic.views.rest.getpodcasts import GetPodcasts
from . import buildCmd, checkResp


def testGetPodCasts(session):
    cmd = buildCmd(session, GetPodcasts, {})
    checkResp(cmd.req, cmd())
