import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.sql.expression import func as dbfunc

from . import Command, addCmd, fillTrack, year_t
from ...models import Album, Track


class GetRandomSongs(Command):
    name = "getRandomSongs.view"
    param_defs = {
        "size": {"default": 10, "type": int},
        "genre": {},
        "fromYear": {"type": year_t},
        "toYear": {"type": year_t},
        "musicFolderId": {},
        }
    dbsess = True


    def handleReq(self, session):
        random_songs = ET.Element("randomSongs")
        fy = self.params["fromYear"]
        ty = self.params["toYear"]
        if fy and ty:
            rows = (session.query(Track).options(subqueryload("*")).
                    join(Album).filter(Album.release_date >= fy and
                                       Album.release_date <= ty).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif fy:
            rows = (session.query(Track).options(subqueryload("*")).
                    join(Album).filter(Album.release_date >= fy).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif ty:
            rows = (session.query(Track).options(subqueryload("*")).
                    join(Album).filter(Album.release_date <= ty).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        else:
            rows = (session.query(Track).options(subqueryload("*")).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        for row in rows:
            song = fillTrack(session, row)
            random_songs.append(song)
        return self.makeResp(child=random_songs)


addCmd(GetRandomSongs)
