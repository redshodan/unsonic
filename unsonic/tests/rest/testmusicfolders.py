import os, unittest, transaction

from pyramid import testing

from . import RestTestCase
from ... import db
from ...models import DBSession
from ...views.rest.getmusicfolders import GetMusicFolders
from ...views.rest import Command


class TestMusicFolders(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetMusicFolders)
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        folders = sub_resp.find("musicFolders")
        for folder in folders.iter("musicFolder"):
            self.assertTrue(folder.get("id").startswith("fl-"))
            self.assertTrue(len(folder.get("name")) > 0)
