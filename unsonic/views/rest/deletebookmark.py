import xml.etree.ElementTree as ET

from . import Command, registerCmd, bookmark_t
from ...models import Bookmark


@registerCmd
class DeleteBookmark(Command):
    name = "deleteBookmark.view"
    param_defs = {
            "id": {"type": bookmark_t, "required": True},
    }
    dbsess = True


    def handleReq(self, session):
        session.query(Bookmark).filter(Bookmark.id == self.params["id"]).delete()
        return self.makeResp()
