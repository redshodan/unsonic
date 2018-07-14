import datetime
from . import Command, registerCmd, MissingParam, track_t
from ...models import Track, Bookmark


@registerCmd
class CreateBookmark(Command):
    name = "createBookmark.view"
    param_defs = {
        "id": {"type": track_t, "required": True},
        "position": {"type": int, "required": True},
        "comment": {"type": str},
        }
    dbsess = True


    def handleReq(self, session):
        id = self.params["id"]

        track = session.query(Track).filter(Track.id == id).one_or_none()
        if track is None:
            raise MissingParam("Invalid id: tr-%s" % id)

        bm = session.query(Bookmark).filter(
            Bookmark.user_id == self.req.authed_user.id,
            Bookmark.track_id == id).one_or_none()
        if bm is None:
            # New creation case
            bm = Bookmark(user_id=self.req.authed_user.id,
                          position=self.params["position"],
                          comment=self.params["comment"],
                          track_id=id)
            session.add(bm)
        else:
            # Update/append case
            bm.position = self.params["position"]
            bm.comment = self.params["comment"]
            bm.changed = datetime.datetime.now()

        return self.makeResp()
