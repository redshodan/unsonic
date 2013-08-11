import os, unittest, transaction
import xml.etree.ElementTree as ET

from pyramid import testing

import mishmash
from mishmash.database import DBInfo, Database

from ...models import DBSession
from ... import dbMain


class RestTestCase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def buildCmd(self, klass, req=None):
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        cmd = klass(request)
        cmd.settings = {"mishmash.paths":"Music: test/music"}
        return cmd

    def checkResp(self, req, resp, ok=True):
        sub_resp = ET.fromstring(resp.body)
        if ok is True:
            self.assertEqual(sub_resp.get("status"), "ok")
        else:
            self.assertEqual(sub_resp.get("status"), "failed")
            error = sub_resp.find("error")
            self.assertEqual(error.get("code"), ok[0])
        return sub_resp

    @classmethod
    def setUpClass(klass):
        try:
            os.unlink("build/testing.sqlite")
        except OSError, e:
            if e.errno != 2:
                raise
        try:
            dbMain(["-c", "testing.ini", "init"])
            dbMain(["-c", "testing.ini", "sync"])
        finally:
            DBSession.remove()
