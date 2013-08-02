from . import Command, addCmd, fillAlbum, fillArtist, fillSong
import xml.etree.ElementTree as ET
from  sqlalchemy.sql.expression import func

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetRandomSongs(Command):
    def __init__(self):
        super(GetRandomSongs, self).__init__("getRandomSongs")
        
    def handleReq(self, req):
        # Param handling
        size, genre, from_year, to_year, music_folder_id = \
          self.getParams(req, (("size", 10), ("genre", None), ("fromYear", None),
                               ("toYear", None), ("musicFolderId", None)))
        
        # Processing
        session = self.mash_db.Session()
        random_songs = ET.Element("randomSongs")
        for row in session.query(Track).order_by(func.random()).limit(size):
            song = fillSong(row)
            random_songs.append(song)
        return self.makeResp(req, child=random_songs)


addCmd(GetRandomSongs())
