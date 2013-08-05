import os, unittest, transaction

from pyramid import testing

from mishmash.orm import Track, Artist, Album, Meta, Label

from . import RestTestCase
from ... import db
from ...models import DBSession
from ...views.rest.stream import Stream
from ...views.rest import Command


class TestStream(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(Stream)
        cmd.req.params["id"] = "tr-1"
        resp = cmd()
        session = self.mash_db.Session()
        row = session.query(Track).filter(Track.id == 1).all()[0]
        streamed = open(row.path).read()
        self.assertEqual(len(resp.body), len(streamed))
        self.assertEqual(resp.body, streamed)
    
    def testNoID(self):
        cmd = self.buildCmd(Stream)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
