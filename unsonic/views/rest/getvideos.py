import xml.etree.ElementTree as ET

from . import Command, registerCmd


# Stubbed out, not implementing
@registerCmd
class GetVideos(Command):
    name = "getVideos.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        return self.makeResp(child=ET.Element("videos"))
