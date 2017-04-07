from unsonic.views.rest.ping import Ping
from . import buildCmd, checkResp


def testBasic(session, ptesting):
    cmd = buildCmd(session, Ping)
    checkResp(cmd.req, cmd())
