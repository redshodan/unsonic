import os

from pyramid import testing

from . import RestTestCase, setUpModule
from ... import mash
from ...models import Session
from ...views.rest.getcoverart import GetCoverArt
from ...views.rest import Command


class TestCoverArt(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetCoverArt, {"id": "al-1"})
        resp = cmd()
        path = os.path.join(list(mash.getPaths(cmd.settings).values())[0],
                            "artist1/ar1al1/cover-back.png")
        fp = open(path, "rb")
        art = fp.read()
        fp.close()
        self.assertEqual(len(resp.body), len(art))
        self.assertEqual(resp.body, art)
    
    def testNoID(self):
        cmd = self.buildCmd(GetCoverArt)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
