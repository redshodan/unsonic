import transaction, datetime
import xml.etree.ElementTree as ET

from . import Command, addCmd, playable_id_t, InternalError, MissingParam
from ...models import (getUserByName, DBSession, PlayList, PlayListTrack, Track,
                       rateItem)


class Star(Command):
    name = "star.view"
    param_defs = {
        "id": {"type":playable_id_t},
        "ablumId": {"type":playable_id_t},
        "artistId": {"type":playable_id_t},
        }
    
    def handleReq(self):
        if self.params["id"]:
            id = self.params["id"]
        elif self.params["albumId"]:
            id = self.params["albumId"]
        elif self.params["artistId"]:
            id = self.params["artistId"]
        else:
            raise MissingParam("Missing a valid id parameter")

        rateItem(self.req.authed_user.id, id, starred=datetime.datetime.now())
        return self.makeResp()


addCmd(Star)