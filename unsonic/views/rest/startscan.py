import xml.etree.ElementTree as ET

from ... import sync
from . import Command, registerCmd


@registerCmd
class StartScan(Command):
    name = "startScan.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        status = ET.Element("scanStatus")
        scanning, count = sync.startSync(session)
        status.set("scanning", "true" if scanning else "false")
        status.set("count", str(count))
        return self.makeResp(child=status)
