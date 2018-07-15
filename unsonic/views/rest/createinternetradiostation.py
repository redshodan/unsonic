import xml.etree.ElementTree as ET

from . import Command, registerCmd, fillInternetRadio
from ...models import InternetRadio


@registerCmd
class CreateInternetRadioStation(Command):
    name = "createInternetRadioStation.view"
    param_defs = {
        "name": {"type": str, "required": True},
        "streamUrl": {"type": str, "required": True},
        "homepageUrl": {"type": str},
        }
    dbsess = True


    def handleReq(self, session):
        ir = InternetRadio(user_id=self.req.authed_user.id,
                           name=self.params["name"],
                           stream_url=self.params["streamUrl"],
                           homepage_url=self.params["homepageUrl"])
        session.add(ir)
        session.flush()

        irs = ET.Element("internetRadioStations")
        irs.append(fillInternetRadio(session, ir))

        return self.makeResp(child=irs)
