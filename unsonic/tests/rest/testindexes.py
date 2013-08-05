import unittest
import transaction

from pyramid import testing

from . import RestTestCase
from ...models import DBSession
from ...views.rest.getindexes import GetIndexes
from ...views.rest import Command


class TestIndexes(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetIndexes)
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        indexes = sub_resp.find("indexes")
        for index in indexes.iter("index"):
            index_name = index.get("name")
            for artist in index.iter("artist"):
                self.assertTrue(artist.get("id").startswith("ar-"))
                self.assertTrue(len(artist.get("name")) > 0)
                self.assertEqual(artist.get("name")[0].upper(), index_name)
                self.assertEqual(artist.get("coverArt"), artist.get("id"))
                self.assertTrue(int(artist.get("albumCount")) >= 0)
