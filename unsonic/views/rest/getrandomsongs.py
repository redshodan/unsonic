from . import Command, addCmd, fillAlbum, fillArtist, fillSong
import xml.etree.ElementTree as ET
from  sqlalchemy.sql.expression import func as dbfunc

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetRandomSongs(Command):
    def __init__(self):
        super(GetRandomSongs, self).__init__("getRandomSongs")
        self.param_defs = {
            "size": {"type": int},
            "genre": {},
            "fromYear": {},
            "toYear": {},
            "musicFolderId": {},
            }
        
    def handleReq(self, req):
        session = self.mash_db.Session()
        random_songs = ET.Element("randomSongs")
        for row in session.query(Track).order_by(dbfunc.random()).\
                       limit(self.params["size"]):
            song = fillSong(row)
            random_songs.append(song)
        return self.makeResp(req, child=random_songs)


addCmd(GetRandomSongs())
