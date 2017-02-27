from . import RestTestCase
from unsonic.views.rest.ping import Ping


class TestPing(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(Ping)
        resp = cmd()
        self.checkResp(cmd.req, resp)
