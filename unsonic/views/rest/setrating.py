import xml.etree.ElementTree as ET

from . import Command, addCmd, playable_id_t, InternalError, MissingParam
from ...models import Session, PlayList, PlayListTrack, Track, rateItem


class SetRating(Command):
    name = "setRating.view"
    param_defs = {
        "id": {"type":playable_id_t, "required":True},
        "rating": {"type":int, "required":True},
        }
    dbsess = True

    
    def handleReq(self, session):
        rateItem(session, self.req.authed_user.id, self.params["id"],
                 rating=self.params["rating"])
        return self.makeResp()


addCmd(SetRating)
