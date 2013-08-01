import xml.etree.ElementTree as ET

from . import Command, addCmd
from ... import db


class GetMusicFolders(Command):
    def __init__(self):
        super(GetMusicFolders, self).__init__("getMusicFolders")
        
    def handleReq(self, req):
        folders = ET.Element("musicFolders")
        count = 0
        for name, path in db.getMashPaths(self.mash_settings).iteritems():
            count = count + 1
            folder = ET.Element("musicFolder")
            folders.append(folder)
            folder.set("id", str(count))
            folder.set("name", name)
        return self.makeResp(req, child=folders)
        
        
addCmd(GetMusicFolders())
