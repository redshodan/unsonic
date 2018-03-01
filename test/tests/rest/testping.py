from unsonic.views.rest.ping import Ping
from . import buildCmd, checkResp


def testBasic(session):
    cmd = buildCmd(session, Ping)
    checkResp(cmd.req, cmd())
