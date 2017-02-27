# import os
import unittest

from . import RestTestCase
from unsonic.views.rest.getcoverart import GetCoverArt
from unsonic.views.rest import Command


class TestCoverArt(RestTestCase):
    @unittest.skip("Get the paths from the db")
    def testBasic(self):
        cmd = self.buildCmd(GetCoverArt, {"id": "al-1"})
        resp = cmd()
        path = os.path.join(list(getMashPaths(cmd.settings).values())[0],
                            "artist 1/artist.png")
        fp = open(path, "rb")
        art = fp.read()
        fp.close()
        self.assertEqual(len(resp.body), len(art))
        self.assertEqual(resp.body, art)


    def testNoID(self):
        cmd = self.buildCmd(GetCoverArt)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
