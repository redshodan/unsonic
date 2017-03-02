import xml.etree.ElementTree as ET

from . import (Command, registerCmd, fillArtistUser, fillAlbumUser,
               fillTrackUser, folder_t)
from ...models import ArtistRating, AlbumRating, TrackRating


@registerCmd
class GetStarred(Command):
    name = "getStarred.view"
    param_defs = {"musicFolderId": {"type": folder_t}}
    dbsess = True


    def handleReq(self, session):
        if self.params["musicFolderId"]:
            lib_id = self.params["musicFolderId"]
        else:
            lib_id = None

        starred = ET.Element("starred")
        # Artists
        for row in session.query(ArtistRating).filter(
                ArtistRating.starred is not None).all():
            if lib_id is None or row.artist.lib_id == lib_id:
                artist = fillArtistUser(session, row.artist, row,
                                        self.req.authed_user)
                starred.append(artist)

        # Albums
        for row in session.query(AlbumRating).filter(
                AlbumRating.starred is not None).all():
            if lib_id is None or row.album.lib_id == lib_id:
                album = fillAlbumUser(session, row.album, row,
                                      self.req.authed_user)
                starred.append(album)

        # Tracks
        for row in session.query(TrackRating).filter(
                TrackRating.starred is not None).all():
            if lib_id is None or row.track.lib_id == lib_id:
                album = fillTrackUser(session, row.track, row,
                                      self.req.authed_user)
                starred.append(album)

        return self.makeResp(child=starred)
