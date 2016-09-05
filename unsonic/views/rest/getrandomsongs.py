import xml.etree.ElementTree as ET
from  sqlalchemy.sql.expression import func as dbfunc

from . import Command, addCmd, fillAlbum, fillArtist, fillSong
from ...models import Session, Artist, Album, Track


class GetRandomSongs(Command):
    name = "getRandomSongs.view"
    param_defs = {
        "size": {"default": 10, "type": int},
        "genre": {},
        "fromYear": {},
        "toYear": {},
        "musicFolderId": {},
        }
    dbsess = True


    def handleReq(self, session):
        random_songs = ET.Element("randomSongs")
        for row in session.query(Track).order_by(dbfunc.random()).\
                       limit(self.params["size"]):
            song = fillSong(row)
            random_songs.append(song)
        return self.makeResp(child=random_songs)


addCmd(GetRandomSongs)
