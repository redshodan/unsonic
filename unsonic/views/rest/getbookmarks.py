import xml.etree.ElementTree as ET

from . import Command, registerCmd, fillBookmark
from ...models import Bookmark


@registerCmd
class GetBookmarks(Command):
    name = "getBookmarks.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        bms = ET.Element("bookmarks")
        for bmrow in session.query(Bookmark).filter(
                Bookmark.user_id == self.req.authed_user.id).all():
            bms.append(fillBookmark(session, bmrow))

        return self.makeResp(child=bms)
