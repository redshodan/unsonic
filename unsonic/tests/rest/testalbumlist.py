import xml.etree.ElementTree as ET

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session
from ...views.rest.getalbumlist import GetAlbumList
from ...views.rest import Command


class TestAlbumList(RestTestCase):
    def validate(self, cmd, resp):
        sub_resp = self.checkResp(cmd.req, resp)
        alist = sub_resp.find("{http://subsonic.org/restapi}albumList")
        count = 0
        titles = []
        for album in alist.iter("{http://subsonic.org/restapi}album"):
            count += 1
            titles.append(album.get("title"))
            self.assertTrue(album.get("id").startswith("al-"))
            self.assertTrue(len(album.get("title")) > 0)
            self.assertEqual(album.get("isDir"), "true")
        return count, titles
        
    def testRandom(self):
        cmd = self.buildCmd(GetAlbumList, {"type": "random"})
        resp = cmd()
        count1, titles1 = self.validate(cmd, resp)
        
    def testSized(self):
        cmd = self.buildCmd(GetAlbumList, {"type": "random", "size": "2"})
        resp = cmd()
        count, titles = self.validate(cmd, resp)
        self.assertEqual(count, 2)

    def testOffset(self):
        cmd = self.buildCmd(GetAlbumList, {"type": "random", "size": "3",
                                           "offset": "1"})
        resp = cmd()
        count, titles = self.validate(cmd, resp)
        self.assertEqual(count, 2)
        
    def testOffset2(self):
        cmd = self.buildCmd(GetAlbumList, {"type": "random", "size": "3",
                                           "offset": "2"})
        resp = cmd()
        count, titles = self.validate(cmd, resp)
        self.assertEqual(count, 1)

    def testNewest(self):
        cmd = self.buildCmd(GetAlbumList, {"type": "newest"})
        resp = cmd()
        count1, titles1 = self.validate(cmd, resp)
            
        cmd = self.buildCmd(GetAlbumList, {"type": "newest"})
        resp = cmd()
        count2, titles2 = self.validate(cmd, resp)
            
        self.assertEqual(titles1, titles2)
        
    def testNoType(self):
        cmd = self.buildCmd(GetAlbumList)
        resp = cmd()
        self.checkResp(cmd.req, resp, Command.E_MISSING_PARAM)
