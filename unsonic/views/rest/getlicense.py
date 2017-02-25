import time
from datetime import datetime
import xml.etree.ElementTree as ET

from . import Command, registerCmd


@registerCmd
class GetLicense(Command):
    name = "getLicense.view"
    param_defs = {}

    def handleReq(self):
        license = ET.Element("license")
        license.set("valid", "true")
        license.set("email", "foo@bar.com")
        now = datetime.fromtimestamp(time.time() + 31536000)
        license.set("licenseExpires", now.isoformat())
        return self.makeResp(child=license)
