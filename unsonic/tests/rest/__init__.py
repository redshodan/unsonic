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
        self.mash_db = the_mash_db

    def tearDown(self):
        testing.tearDown()

    def buildCmd(self, klass, req=None):
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        cmd = klass(request)
        cmd.mash_db = self.mash_db
        cmd.mash_settings = {"music.paths":"Music: test/music"}
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
            os.unlink("build/testing-mishmash.sqlite")
        except OSError, e:
            if e.errno != 2:
                raise
        try:
            dbMain(["init", "testing.ini"])
            dbMain(["sync", "testing.ini"])
        finally:
            DBSession.remove()
        global the_mash_db
        db_uri = "sqlite:///%s/build/testing-mishmash.sqlite" % os.getcwd()
        the_mash_db = Database(DBInfo(uri=db_uri))
