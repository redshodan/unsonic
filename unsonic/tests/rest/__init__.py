import os, shutil, unittest, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from webob.multidict import MultiDict, NestedMultiDict
from pyramid import testing

# from ... import dbMain, models
from ... import models


XMLLINT_TEST = \
"""<?xml version="1.0" encoding="UTF-8"?>
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok"
                   unsonic="0.0" version="1.14.0"/>
"""


class RestTestCase(unittest.TestCase):
    def setUp(self):
        shutil.copyfile("build/testing.sqlite.org", "build/testing.sqlite")
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def buildCmd(self, klass, params={}):
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        md = MultiDict()
        for key, val in params.items():
            md.add(key, val)
        request.params = NestedMultiDict(md)
        with models.Session() as session:
            request.authed_user = models.getUserByName(session, "test")
        cmd = klass(request)
        cmd.settings = {"mishmash.paths":"Music: test/music"}
        return cmd

    def checkResp(self, req, resp, ok=True):
        sub_resp = ET.fromstring(resp.body)

        # Validate the response against the XSD
        p = subprocess.Popen(["xmllint", "--format", "--schema",
                              "xsd/unsonic-subsonic-api.xsd", "-"],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        out, err = p.communicate(resp.body, timeout=15)
        if p.returncode:
            self.fail(out.decode("utf-8"))

        # Validate the return type
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

    print("\nSetting up test database...")

    # Check for xmllint
    p = subprocess.Popen(["xmllint", "--format", "--schema",
                          "xsd/unsonic-subsonic-api.xsd", "-"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out, err = p.communicate(XMLLINT_TEST.encode("utf-8"), timeout=15)
    if p.returncode:
        raise Exception("xmllint is required for the tests: " +
                        out.decode("utf-8"))

    # Build a fresh mishmash db
    db = Path("build/testing.sqlite")
    if db.exists():
        db.unlink()
    dbMain(["-c", "testing.ini", "init"])
    dbMain(["-c", "testing.ini", "sync"])
    dbMain(["-c", "testing.ini", "adduser", "test", "test"])
    db.rename("build/testing.sqlite.org")
    
    print("Test setup complete\n")
