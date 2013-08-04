from . import Command, NotFound, addCmd, artist_t, fillAlbum, fillArtist
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetArtist(Command):
    name = "getArtist.view"
    param_defs = {"id": {"required": True, "type": artist_t}}

    def handleReq(self):
        session = self.mash_db.Session()
        artist = None
        for row in session.query(Artist).\
                       filter(Artist.id == self.params["id"]).all():
            artist = fillArtist(row)
        if artist is None:
            raise NotFound(self.req.params["id"])
        album_count = 0
        for row in session.query(Album).filter(
                Album.artist_id == self.params["id"]).all():
            print("FOO")
            album_count = album_count + 1
            album = fillAlbum(row)
            artist.append(album)
        for album in artist:
            song_count = 0
            duration = 0
            for row in session.query(Track).filter(
                    Track.album_id == int(album.get("id")[3:])).all():
                song_count = song_count + 1
                duration = duration + row.time_secs
            album.set("songCount", str(song_count))
            album.set("duration", str(duration))
        artist.set("albumCount", str(album_count))
        return self.makeResp(child=artist)


addCmd(GetArtist)
