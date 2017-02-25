import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import Command, registerCmd, fillArtistUser, fillAlbumUser, fillTrackUser
from ...models import ArtistRating, AlbumRating, TrackRating


@registerCmd
class GetStarred(Command):
    name = "getStarred.view"
    param_defs = {"musicFolderId": {}}
    dbsess = True


    def handleReq(self, session):
        starred = ET.Element("starred")

        # Artists
        for row in session.query(ArtistRating).options(subqueryload("*")). \
                       filter(ArtistRating.starred is not None).all():
            artist = fillArtistUser(session, row.artist, row,
                                    self.req.authed_user)
            starred.append(artist)

        # Albums
        for row in session.query(AlbumRating).options(subqueryload("*")). \
                       filter(AlbumRating.starred is not None).all():
            album = fillAlbumUser(session, row.album, row, self.req.authed_user)
            starred.append(album)

        # Tracks
        for row in session.query(TrackRating).options(subqueryload("*")). \
                       filter(TrackRating.starred is not None).all():
            album = fillTrackUser(session, row.track, row, self.req.authed_user)
            starred.append(album)

        return self.makeResp(child=starred)
