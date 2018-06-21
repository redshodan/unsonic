from unsonic.views.rest.star import Star
from unsonic.views.rest.unstar import UnStar
from . import buildCmd, checkResp


def testUnStar(session):
    cmd = buildCmd(session, Star, {"id": "tr-1"})
    checkResp(cmd.req, cmd())

    cmd = buildCmd(session, UnStar, {"id": "tr-1"})
    checkResp(cmd.req, cmd())
