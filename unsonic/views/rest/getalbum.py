import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import (Command, MissingParam, NotFound, addCmd, album_t, fillAlbumID3,
               fillTrackUser)
from ...models import Session, Artist, Album, Track


class GetAlbum(Command):
    name = "getAlbum.view"
    param_defs = {"id": {"required": True, "type": album_t}}
    dbsess = True


    def handleReq(self, session):
        album = None
        for row in session.query(Album).options(subqueryload("*")).\
                       filter(Album.id == self.params["id"]).all():
            album = fillAlbumID3(session, row, self.req.authed_user, True)
        if album is None:
            raise NotFound(self.req.params["id"])
        return self.makeResp(child=album)

        
addCmd(GetAlbum)
