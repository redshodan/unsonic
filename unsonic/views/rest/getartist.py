from . import (Command, registerCmd, NotFound, artist_t, fillAlbumID3,
               fillArtistUser)
from ...models import Artist, Album, Track


@registerCmd
class GetArtist(Command):
    name = "getArtist.view"
    param_defs = {"id": {"required": True, "type": artist_t}}
    dbsess = True


    def handleReq(self, session):
        artist = None
        for row in session.query(Artist).filter(
                Artist.id == self.params["id"]).all():
            artist = fillArtistUser(session, row, None, self.req.authed_user)
        if artist is None:
            raise NotFound(self.req.params["id"])
        album_count = 0
        for row in session.query(Album).filter(
                Album.artist_id == self.params["id"]).all():
            album_count += 1
            album = fillAlbumID3(session, row, self.req.authed_user, False)
            artist.append(album)
        for album in artist:
            if album.tag != "album":
                continue
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
