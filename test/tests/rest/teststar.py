from unsonic.views.rest.star import Star
from . import buildCmd, checkResp


def testStar(session):
    cmd = buildCmd(session, Star, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
