import xml.etree.ElementTree as ET

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session
from ...views.rest.getmusicdirectory import GetMusicDirectory
from ...views.rest import Command


class TestMusicDirectory(RestTestCase):
    def testArtistOneAlbum(self):
        aid = "ar-4"
        cmd = self.buildCmd(GetMusicDirectory, {"id": aid})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        directory = sub_resp.find("{http://subsonic.org/restapi}directory")
        self.assertEqual(directory.get("id"), aid)
        self.assertTrue(len(directory.get("name")) > 0)
        self.assertEqual(directory.get("parent"), "fl-Music")
        for child in directory.iter("{http://subsonic.org/restapi}child"):
            self.assertTrue(child.get("id").startswith("al-"))
            self.assertTrue(len(child.get("title")) > 0)
            self.assertTrue(len(child.get("artist")) > 0)
            self.assertEqual(child.get("isDir"), "true")
            self.assertEqual(child.get("parent"), directory.get("id"))

    def testArtistNoAlbums(self):
        aid = "ar-2"
        cmd = self.buildCmd(GetMusicDirectory, {"id": aid})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        directory = sub_resp.find("{http://subsonic.org/restapi}directory")
        self.assertEqual(directory.get("id"), aid)
        self.assertTrue(len(directory.get("name")) > 0)
        self.assertEqual(directory.get("parent"), "fl-Music")
        child = directory.find("{http://subsonic.org/restapi}child")
        self.assertEqual(child.get("album"), "-")
        self.assertTrue(child.get("id").startswith("tr-"))

    def testAlbum(self):
        aid = "al-1"
        cmd = self.buildCmd(GetMusicDirectory, {"id": aid})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        directory = sub_resp.find("{http://subsonic.org/restapi}directory")
        self.assertEqual(directory.get("id"), aid)
        self.assertTrue(len(directory.get("name")) > 0)
        self.assertTrue(directory.get("parent").startswith("ar-"))
        for child in directory.iter("{http://subsonic.org/restapi}child"):
            self.assertTrue(child.get("id").startswith("tr-"))
            self.assertTrue(len(child.get("title")) > 0)
            self.assertTrue(len(child.get("artist")) > 0)
            self.assertTrue(len(child.get("album")) > 0)
            self.assertEqual(child.get("coverArt"), aid)
            self.assertEqual(child.get("isDir"), "false")
            self.assertEqual(child.get("parent"), directory.get("id"))

    def testArtistNotFound(self):
        cmd = self.buildCmd(GetMusicDirectory, {"id": "ar-1000000000000"})
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_NOT_FOUND)

    def testAlbumNotFound(self):
        cmd = self.buildCmd(GetMusicDirectory, {"id": "ar-1000000000000"})
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_NOT_FOUND)
            
    def testBadID(self):
        cmd = self.buildCmd(GetMusicDirectory, {"id": "foobar"})
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)

    def testNoID(self):
        cmd = self.buildCmd(GetMusicDirectory)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
