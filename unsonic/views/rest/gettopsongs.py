import xml.etree.ElementTree as ET

from . import Command, registerCmd, int_t


# TODO: Actually implement
@registerCmd
class GetTopSongs(Command):
    name = "getTopSongs.view"
    param_defs = {
        "artist": {"required": True},
        "count": {"default": 50, "type": int_t},
        }
    dbsess = True


    # Actually do this for realz once last.fm stuff is hooked up
    def handleReq(self, session):
        songs = ET.Element("topSongs")
        return self.makeResp(child=songs)
