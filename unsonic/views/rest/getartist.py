from . import (Command, registerCmd, NotFound, artist_t, fillAlbumID3,
               fillArtistUser)
from ...models import Artist, Album, Track


@registerCmd
class GetArtist(Command):
    name = "getArtist.view"
    param_defs = {"id": {"required": True, "type": artist_t}}
    dbsess = True


    def handleReq(self, session):
        # Get the multiple artists
        artists = []
        for pid in self.params["id"]:
            row = session.query(Artist).filter(Artist.id == pid).one_or_none()
            if row is None:
                raise NotFound(self.req.params["id"])
            artists.append(row)

        # Assert that they have the same name
        first = artists[0]
        for row in artists:
            if first.name != row.name:
                raise NotFound(self.req.params["id"])

        # Now fill and merge the artists
        artist = fillArtistUser(session, artists, None, self.req.authed_user)
        album_count = 0
        for ar_row in artists:
            for row in session.query(Album).filter(
                    Album.artist_id == ar_row.id).all():
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
