from unsonic.views.rest.setrating import SetRating
from . import buildCmd, checkResp


def testSetRating(session):
    cmd = buildCmd(session, SetRating, {"id": "tr-1", "rating": "3"})
    checkResp(cmd.req, cmd())
