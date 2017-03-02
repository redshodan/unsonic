from . import Command, registerCmd, NotFound, album_t, fillAlbumID3
from ...models import Album


@registerCmd
class GetAlbum(Command):
    name = "getAlbum.view"
    param_defs = {"id": {"required": True, "type": album_t}}
    dbsess = True


    def handleReq(self, session):
        album = None
        for row in session.query(Album).filter(
                Album.id == self.params["id"]).all():
            album = fillAlbumID3(session, row, self.req.authed_user, True)
        if album is None:
            raise NotFound(self.req.params["id"])
        return self.makeResp(child=album)
