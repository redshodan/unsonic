import transaction
import xml.etree.ElementTree as ET

from . import Command, addCmd, InternalError, MissingParam
from ...models import getUserByName, DBSession, PlayList, PlayListTrack, Track


class Scrobble(Command):
    name = "scrobble.view"
    param_defs = {
        "id": {"required": True},
        "time": {},
        "submission": {},
        }
    
    def handleReq(self):
        # FIXME do something here
        return self.makeResp()


addCmd(Scrobble)
