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
            ret = session.query(Album).filter(Album.id == row.album_id).all()
            if len(ret) == 1:
                album_name = ret[0].title
                album_date = str(ret[0].release_date) if ret[0].release_date \
                                 else ""
            else:
                album_name = None
                album_date = None
            ret = session.query(Artist).filter(Artist.id == row.artist_id).all()
            artist_name = ret[0].name if len(ret) else ""
            song = fillSong(row, album_name=album_name, album_date=album_date)
            random_songs.append(song)
        return self.makeResp(req, child=random_songs)


addCmd(GetRandomSongs())
