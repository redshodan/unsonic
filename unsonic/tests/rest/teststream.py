import unittest

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session, Track
from ...views.rest.stream import Stream
from ...views.rest import Command


class TestStream(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(Stream)
        cmd.req.params["id"] = "tr-1"
        resp = cmd()
        with Session() as session:
            row = session.query(Track).filter(Track.id == 1).all()[0]
            fp = open(row.path, "rb")
            streamed = fp.read()
            fp.close()
        self.assertEqual(len(resp.body), len(streamed))
        self.assertEqual(resp.body, streamed)
    
    def testNoID(self):
        cmd = self.buildCmd(Stream)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
