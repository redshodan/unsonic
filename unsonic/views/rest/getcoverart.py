import os.path

from pyramid.response import Response
from pyramid.exceptions import NotFound

from . import Command, addCmd
from ...models import DBSession, Artist, Album, Track, Image
from ... import mash


class GetCoverArt(Command):
    name = "getCoverArt.view"
    param_defs = {"id": {"required": True}}

    def handleReq(self):
        id = self.params["id"]
        num = int(id[3:])
        row = None
        if id.startswith("ar-") or id.startswith("al-"):
            image = DBSession.query(Image).filter_by(id=num).all()

        if len(image) == 1:
            return Response(content_type=image[0].mime_type.encode("latin1"),
                            body=image[0].data)
        else:
            raise NotFound()


addCmd(GetCoverArt)
