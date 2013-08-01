from . import Command, addCmd, fillAlbum, fillArtist
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetArtist(Command):
    def __init__(self):
        super(GetArtist, self).__init__("getArtist")
        
    def handleReq(self, req):
        if "id" not in req.params:
            return self.makeResp(req, status=Command.E_MISSING_PARAM)
        artist_id = int(req.params["id"])
        session = self.mash_db.Session()
        for row in session.query(Artist).filter(Artist.id == artist_id).all():
            artist = fillArtist(row)
            artist_name = row.name
        album_count = 0
        for row in session.query(Album).filter(
                Album.artist_id == artist_id).all():
            album_count = album_count + 1
            album = fillAlbum(row, artist_name)
            artist.append(album)
        for album in artist:
            song_count = 0
            duration = 0
            for row in session.query(Track).filter(
                    Track.album_id == int(album.get("id"))).all():
                song_count = song_count + 1
                duration = duration + row.time_secs
            album.set("songCount", str(song_count))
            album.set("duration", str(duration))
        artist.set("albumCount", str(album_count))
        return self.makeResp(req, child=artist)


addCmd(GetArtist())
