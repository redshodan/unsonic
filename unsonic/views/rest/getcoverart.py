import os.path

from pyramid.response import FileResponse
from pyramid.exceptions import NotFound

from . import Command, addCmd
from ...models import DBSession, Artist, Album, Track, AlbumArt
from ... import mash


class GetCoverArt(Command):
    name = "getCoverArt.view"
    param_defs = {"id": {"required": True}}

    # FIXME: Do this right once there is art info in mishmash
    def handleReq(self):
        id = self.params["id"]
        num = int(id[3:])
        if id.startswith("ar-"):
            art = DBSession.query(ArtistArt).filter_by(id=num).all()
        if id.startswith("al-"):
            art = DBSession.query(AlbumArt).filter_by(id=num).all()
        if len(art) == 1:
            return FileResponse(art[0].path)
        else:
            raise NotFound()


addCmd(GetCoverArt)
