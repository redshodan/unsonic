import xml.etree.ElementTree as ET

from ... import sync
from . import Command, registerCmd


@registerCmd
class GetScanStatus(Command):
    name = "getScanStatus.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        status = ET.Element("scanStatus")
        scanning, count = sync.syncStatus(session)
        status.set("scanning", "true" if scanning else "false")
        status.set("count", str(count))
        return self.makeResp(child=status)
