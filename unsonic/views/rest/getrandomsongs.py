import xml.etree.ElementTree as ET

from sqlalchemy.sql.expression import func as dbfunc

from . import Command, registerCmd, fillTrack, year_t, folder_t, int_t
from ...models import Album, Track


@registerCmd
class GetRandomSongs(Command):
    name = "getRandomSongs.view"
    param_defs = {
        "size": {"default": 10, "type": int_t},
        "genre": {},
        "fromYear": {"type": year_t},
        "toYear": {"type": year_t},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True


    def query(self, session):
        if self.params["musicFolderId"]:
            return (session.query(Track).
                    filter(Track.lib_id == self.params["musicFolderId"]))
        else:
            return session.query(Track)


    def handleReq(self, session):
        random_songs = ET.Element("randomSongs")
        fy = self.params["fromYear"]
        ty = self.params["toYear"]
        if fy and ty:
            rows = (self.query(session).
                    join(Album).filter(Album.release_date >= fy and
                                       Album.release_date <= ty).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif fy:
            rows = (self.query(session).
                    join(Album).filter(Album.release_date >= fy).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif ty:
            rows = (self.query(session).
                    join(Album).filter(Album.release_date <= ty).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        else:
            rows = (self.query(session).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        for row in rows:
            song = fillTrack(session, row)
            random_songs.append(song)
        return self.makeResp(child=random_songs)
