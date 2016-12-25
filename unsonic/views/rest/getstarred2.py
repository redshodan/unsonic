import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import (Command, MissingParam, NotFound, addCmd, fillArtistUser,
               fillAlbumID3, fillTrackUser)
from ...models import (Session, Artist, Album, Track, ArtistRating, AlbumRating,
                       TrackRating)
from ... import mash


class GetStarred2(Command):
    name = "getStarred2.view"
    param_defs = {"musicFolderId": {}}
    dbsess = True


    def handleReq(self, session):
        starred = ET.Element("starred2")
        
        # Artists
        for row in session.query(ArtistRating).options(subqueryload("*")). \
                       filter(ArtistRating.starred is not None).all():
            artist = fillArtistUser(session, row.artist, row,
                                    self.req.authed_user)
            starred.append(artist)

        # Albums
        for row in session.query(AlbumRating).options(subqueryload("*")). \
                       filter(AlbumRating.starred is not None).all():
            album = fillAlbumID3(session, row.album, self.req.authed_user, False)
            starred.append(album)

        # Tracks
        for row in session.query(TrackRating).options(subqueryload("*")). \
                       filter(TrackRating.starred is not None).all():
            album = fillTrackUser(session, row.track, row, self.req.authed_user)
            starred.append(album)
            
        return self.makeResp(child=starred)


addCmd(GetStarred2)
