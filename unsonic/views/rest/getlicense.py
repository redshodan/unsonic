from . import Command, addCmd
import xml.etree.ElementTree as ET


class GetLicense(Command):
    def __init__(self):
        super(GetLicense, self).__init__("getLicense")
        
    def handleReq(self, req):
        # Processing
        license = ET.Element("license")
        license.set("valid", "true")
        license.set("email", "foo@bar.com")
        license.set("key", "0" * 32)
        license.set("date", "2011-07-21T21:08:04")
        return self.makeResp(req, child=license)
        
        
addCmd(GetLicense())
