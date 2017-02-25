import xml.etree.ElementTree as ET

from . import Command, registerCmd


@registerCmd
class GetPodcasts(Command):
    name = "getPodcasts.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        podcasts = ET.Element("podcasts")
        return self.makeResp(child=podcasts)
