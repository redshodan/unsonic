import os, shutil, unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from pyramid import testing

from ... import dbMain, models


class RestTestCase(unittest.TestCase):
    def setUp(self):
        shutil.copyfile("build/testing.sqlite.org", "build/testing.sqlite")
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def buildCmd(self, klass, req=None):
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        with models.Session() as session:
            request.authed_user = models.getUserByName(session, "test")
        cmd = klass(request)
        cmd.settings = {"mishmash.paths":"Music: test/music"}
        return cmd

    def checkResp(self, req, resp, ok=True):
        sub_resp = ET.fromstring(resp.body)
        if ok is True:
            self.assertEqual(sub_resp.get("status"), "ok")
        else:
            self.assertEqual(sub_resp.get("status"), "failed")
            error = sub_resp.find("{http://subsonic.org/restapi}error")
            self.assertEqual(error.get("code"), ok[0])
        return sub_resp


def setUpModule():
    if Path("build/testing.sqlite.org").exists():
        return
    db = Path("build/testing.sqlite")
    if db.exists():
        db.unlink()
    dbMain(["-c", "testing.ini", "init"])
    dbMain(["-c", "testing.ini", "sync"])
    dbMain(["-c", "testing.ini", "adduser", "test", "test"])
    db.rename("build/testing.sqlite.org")
