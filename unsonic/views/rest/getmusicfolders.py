import xml.etree.ElementTree as ET

from . import Command, addCmd
from ... import mash


class GetMusicFolders(Command):
    name = "getMusicFolders.view"
    param_defs = {}

    def handleReq(self):
        folders = ET.Element("musicFolders")
        for name, path in mash.getPaths(self.settings).items():
            folder = ET.Element("musicFolder")
            folders.append(folder)
            folder.set("id", "fl-%s" % name)
            folder.set("name", name)
        return self.makeResp(child=folders)
        
        
addCmd(GetMusicFolders)
