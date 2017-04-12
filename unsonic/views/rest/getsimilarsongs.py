import xml.etree.ElementTree as ET

from . import Command, registerCmd, int_t, track_t


# TODO: Actually implement
@registerCmd
class GetSimilarSongs(Command):
    name = "getSimilarSongs.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        "count": {"default": 50, "type": int_t},
        }
    dbsess = True


    # Actually do this for realz once last.fm stuff is hooked up
    def handleReq(self, session):
        ainfo = ET.Element("similarSongs")
        return self.makeResp(child=ainfo)
