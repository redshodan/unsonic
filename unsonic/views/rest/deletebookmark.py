from . import Command, registerCmd, track_t
from ...models import Bookmark


@registerCmd
class DeleteBookmark(Command):
    name = "deleteBookmark.view"
    param_defs = {
            "id": {"type": track_t, "required": True},
    }
    dbsess = True


    def handleReq(self, session):
        session.query(Bookmark).filter(
            Bookmark.track_id == self.params["id"]).delete()
        return self.makeResp()
