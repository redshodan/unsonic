from . import RestTestCase
from ...views.rest.getmusicfolders import GetMusicFolders


class TestMusicFolders(RestTestCase):
    def testBasic(self):
        cmd = self.buildCmd(GetMusicFolders)
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        folders = sub_resp.find("{http://subsonic.org/restapi}musicFolders")
        for folder in folders.iter("{http://subsonic.org/restapi}musicFolder"):
            self.assertTrue(folder.get("id").startswith("fl-"))
            self.assertTrue(len(folder.get("name")) > 0)
