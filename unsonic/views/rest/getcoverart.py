import os.path

from sqlalchemy.orm import subqueryload

from pyramid.response import Response
from pyramid.exceptions import NotFound

from . import Command, addCmd
from ...models import Session, Artist, Album, Track, Image
from ... import mash


class GetCoverArt(Command):
    name = "getCoverArt.view"
    param_defs = {"id": {"required": True}}
    dbsess = True


    def handleReq(self, session):
        id = self.params["id"]
        num = int(id[3:])
        row = None
        if id.startswith("ar-") or id.startswith("al-"):
            image = session.query(Image).options(subqueryload("*")).\
              filter_by(id=num).all()

        if len(image) == 1:
            return Response(content_type=image[0].mime_type,
                            body=image[0].data)
        else:
            raise NotFound()


addCmd(GetCoverArt)
