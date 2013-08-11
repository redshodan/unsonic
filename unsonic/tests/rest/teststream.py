import os, unittest, transaction

from pyramid import testing

from . import RestTestCase
from ...models import DBSession, Track
from ...views.rest.stream import Stream
from ...views.rest import Command


class TestStream(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(Stream)
        cmd.req.params["id"] = "tr-1"
        resp = cmd()
        row = DBSession.query(Track).filter(Track.id == 1).all()[0]
        streamed = open(row.path).read()
        self.assertEqual(len(resp.body), len(streamed))
        self.assertEqual(resp.body, streamed)
    
    def testNoID(self):
        cmd = self.buildCmd(Stream)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
