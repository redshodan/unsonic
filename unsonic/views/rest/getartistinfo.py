import xml.etree.ElementTree as ET

from . import BACON_IPSUM, Command, registerCmd, int_t, playable_id_t


# TODO: Actually implement
@registerCmd
class GetArtistInfo(Command):
    name = "getArtistInfo.view"
    param_defs = {
        "id": {"required": True, "type": playable_id_t},
        "count": {"default": 20, "type": int_t},
        "includeNotPresent": {},
        }
    dbsess = True


    # Actually do this for realz once last.fm stuff is hooked up
    def handleReq(self, session):
        ainfo = ET.Element("artistInfo")
        bio = ET.Element("biography")
        bio.text = BACON_IPSUM
        ainfo.append(bio)
        mbid = ET.Element("musicBrainzId")
        mbid.text = "1234567890"
        ainfo.append(mbid)

        for name in ["lastFmUrl", "smallImageUrl", "mediumImageUrl",
                     "largeImageUrl"]:
            url = ET.Element(name)
            url.text = "https://foo.com/foo"
            ainfo.append(url)

        return self.makeResp(child=ainfo)
