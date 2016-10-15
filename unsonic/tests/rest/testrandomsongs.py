import unittest

from pyramid import testing

from . import RestTestCase, setUpModule
from ...models import Session
from ...views.rest.getrandomsongs import GetRandomSongs
from ...views.rest import Command


class TestRandomSongs(RestTestCase):
    def validate(self, cmd, resp):
        sub_resp = self.checkResp(cmd.req, resp)
        songs = sub_resp.find("{http://subsonic.org/restapi}randomSongs")
        count = 0
        titles = []
        for song in songs.iter("{http://subsonic.org/restapi}song"):
            count += 1
            titles.append(song.get("title"))
            self.assertTrue(song.get("id").startswith("tr-"))
            self.assertTrue(int(song.get("id")[3:]) > 0)
            self.assertTrue(int(song.get("duration")) >= 0)
            self.assertTrue(int(song.get("bitRate")) >= 0)
        return count, titles
        
    def testBasic(self):
        cmd = self.buildCmd(GetRandomSongs)
        resp = cmd()
        count, titles = self.validate(cmd, resp)
        self.assertEqual(count, 10)
        
    def testSized(self):
        cmd = self.buildCmd(GetRandomSongs)
        cmd.req.params["size"] = "2"
        resp = cmd()
        count, titles = self.validate(cmd, resp)
        self.assertEqual(count, 2)
