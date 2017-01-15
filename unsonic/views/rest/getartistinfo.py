import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import (Command, MissingParam, NotFound, addCmd, playable_id_t)
from ...models import Session, Artist, Album, Track


bacon_ipsum = "Bacon ipsum dolor amet biltong sausage ribeye pancetta salami pork chop. Short loin sirloin burgdoggen, turducken kielbasa corned beef landjaeger chicken short ribs capicola. Drumstick turkey jerky, cow shankle flank pork loin ball tip. Meatball shoulder landjaeger jerky. Bresaola prosciutto alcatra venison, meatloaf pork belly ball tip tail cupim porchetta. Chuck alcatra leberkas tail flank. Kevin chicken strip steak meatball ground round cow."


class GetArtistInfo(Command):
    name = "getArtistInfo.view"
    param_defs = {
        "id": {"required": True, "type": playable_id_t},
        "count": {"default": 20, "type": int},
        "includeNotPresent": {},
        }
    dbsess = True


    # Actually do this for realz once last.fm stuff is hooked up
    def handleReq(self, session):
        ainfo = ET.Element("artistInfo")
        bio = ET.Element("biography")
        bio.text = bacon_ipsum
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

        
addCmd(GetArtistInfo)
