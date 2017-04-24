import xml.etree.ElementTree as ET

from . import BACON_IPSUM, Command, registerCmd, playable_id_t


# TODO: Actually implement
@registerCmd
class GetAlbumInfo(Command):
    name = "getAlbumInfo.view"
    param_defs = {
        "id": {"required": True, "type": playable_id_t},
        }
    dbsess = True


    # Actually do this for realz once last.fm stuff is hooked up
    def handleReq(self, session):
        ainfo = ET.Element("albumInfo")
        notes = ET.Element("notes")
        notes.text = BACON_IPSUM
        ainfo.append(notes)
        mbid = ET.Element("musicBrainzId")
        mbid.text = "1234567890"
        ainfo.append(mbid)

        for name in ["lastFmUrl", "smallImageUrl", "mediumImageUrl",
                     "largeImageUrl"]:
            url = ET.Element(name)
            url.text = "https://foo.com/foo"
            ainfo.append(url)

        return self.makeResp(child=ainfo)
