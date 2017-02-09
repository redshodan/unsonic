from . import RestTestCase
from ...models import Session, PlayList
from ...views.rest.createplaylist import CreatePlayList


class TestCreatePlayList(RestTestCase):
    def testCreatePlayList(self):
        pname = "playlist1"
        plist = ["tr-1", "tr-2", "tr-3"]
        cmd = self.buildCmd(CreatePlayList, {"name": pname, "songId": plist})
        resp = cmd()
        self.checkResp(cmd.req, resp)
        with Session() as session:
            row = session.query(PlayList).\
                      filter(PlayList.name == pname).one_or_none()
            self.assertTrue(row)
            self.assertEqual([t.track_id for t in row.tracks],
                             [int(t.replace("tr-", "")) for t in plist])
            self.assertEqual(row.owner.name, "test")


    def testUpdatePlayList(self):
        pname = "playlist1"
        plist = ["tr-1", "tr-2", "tr-3"]
        cmd = self.buildCmd(CreatePlayList, {"name": pname, "songId": plist})
        sub_resp = self.checkResp(cmd.req, cmd())
        playlist = sub_resp.find("{http://subsonic.org/restapi}playlist")
        pl_id = playlist.get("id")

        plist2 = ["tr-3", "tr-2", "tr-1"]
        cmd = self.buildCmd(CreatePlayList,
                            {"playlistId": pl_id, "songId": plist2})
        self.checkResp(cmd.req, cmd())
        with Session() as session:
            row = session.query(PlayList).\
                      filter(PlayList.name == pname).one_or_none()
            self.assertTrue(row)
            self.assertEqual([t.track_id for t in row.tracks],
                             [int(t.replace("tr-", "")) for t in plist + plist2])
            self.assertEqual(row.owner.name, "test")
