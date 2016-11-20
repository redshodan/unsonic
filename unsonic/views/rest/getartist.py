import xml.etree.ElementTree as ET

from . import Command, NotFound, addCmd, artist_t, fillAlbum, fillArtist
from ...models import Session, Artist, Album, Track


# class GetArtist(Command):
#     name = "getArtist.view"
#     param_defs = {"id": {"required": True, "type": artist_t}}

#     def handleReq(self):
#         artist = None
#         for row in session.query(Artist).options(subqueryload("*")).\
#                        filter(Artist.id == self.params["id"]).all():
#             artist = fillArtist(session, row)
#         if artist is None:
#             raise NotFound(self.req.params["id"])
#         album_count = 0
#         for row in session.query(Album).options(subqueryload("*")).filter(
#                 Album.artist_id == self.params["id"]).all():
#             album_count = album_count + 1
#             album = fillAlbum(session, row)
#             artist.append(album)
#         for album in artist:
#             song_count = 0
#             duration = 0
#             for row in session.query(Track).options(subqueryload("*")).filter(
#                     Track.album_id == int(album.get("id")[3:])).all():
#                 song_count = song_count + 1
#                 duration = duration + row.time_secs
#             album.set("songCount", str(song_count))
#             album.set("duration", str(duration))
#         artist.set("albumCount", str(album_count))
#         return self.makeResp(child=artist)


from .getmusicdirectory import GetMusicDirectory

class GetArtist(GetMusicDirectory):
    name = "getArtist.view"

    def __init__(self, req):
        super(GetArtist, self).__init__(req)
        self.setParams(dir_param="artist", album_param="album",
                       track_param="song")


addCmd(GetArtist)
