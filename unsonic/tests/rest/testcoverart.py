import os, unittest, transaction

from pyramid import testing

from . import RestTestCase
from ... import db
from ...models import DBSession
from ...views.rest.getcoverart import GetCoverArt
from ...views.rest import Command


class TestCoverArt(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetCoverArt)
        cmd.req.params["id"] = "al-1"
        resp = cmd()
        path = os.path.join(db.getMashPaths(cmd.mash_settings).values()[0],
                            "albumart.png")
        art = open(path).read()
        self.assertEqual(len(resp.body), len(art))
        self.assertEqual(resp.body, art)
    
    def testNoType(self):
        cmd = self.buildCmd(GetCoverArt)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
