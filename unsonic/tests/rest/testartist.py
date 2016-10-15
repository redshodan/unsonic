import unittest

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session
from ...views.rest.getartist import GetArtist
from ...views.rest import Command


class TestArtist(RestTestCase):
    def testNoAlbums(self):
        aid = "ar-1"
        cmd = self.buildCmd(GetArtist)
        cmd.req.params["id"] = aid
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        artist = sub_resp.find("{http://subsonic.org/restapi}artist")
        self.assertEqual(artist.get("id"), aid)

    def testTwoAlbums(self):
        aid = "ar-6"
        cmd = self.buildCmd(GetArtist)
        cmd.req.params["id"] = aid
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        artist = sub_resp.find("{http://subsonic.org/restapi}artist")
        self.assertEqual(artist.get("id"), aid)
        for album in artist.iter("{http://subsonic.org/restapi}album"):
            self.assertTrue(album.get("id").startswith("al-"))
            self.assertTrue(int(album.get("id")[3:]) > 0)
            self.assertEqual(album.get("artist"), artist.get("name"))
            self.assertTrue(int(album.get("songCount")) > 0)
            self.assertTrue(int(album.get("duration")) >= 0)

    def testNotFound(self):
        cmd = self.buildCmd(GetArtist)
        cmd.req.params["id"] = "ar-1000000000000"
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_NOT_FOUND)

    def testBadID(self):
        cmd = self.buildCmd(GetArtist)
        cmd.req.params["id"] = "foobar"
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)

    def testNoID(self):
        cmd = self.buildCmd(GetArtist)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
        
