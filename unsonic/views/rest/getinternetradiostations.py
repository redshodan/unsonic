import xml.etree.ElementTree as ET

from . import Command, registerCmd, fillInternetRadio
from ...models import InternetRadio


@registerCmd
class GetInternetRadioStations(Command):
    name = "getInternetRadioStations.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        irs = ET.Element("internetRadioStations")
        query = session.query(InternetRadio).filter(
            InternetRadio.user_id == self.req.authed_user.id)
        for row in query.all():
            irs.append(fillInternetRadio(session, row))

        return self.makeResp(child=irs)
