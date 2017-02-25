import xml.etree.ElementTree as ET

from . import Command, registerCmd
from ... import models


@registerCmd
class GetMusicFolders(Command):
    name = "getMusicFolders.view"
    param_defs = {}

    def handleReq(self):
        folders = ET.Element("musicFolders")
        for name, path in models.getMashPaths(self.settings).items():
            folder = ET.Element("musicFolder")
            folders.append(folder)
            folder.set("id", "fl-%s" % name)
            folder.set("name", name)
        return self.makeResp(child=folders)
