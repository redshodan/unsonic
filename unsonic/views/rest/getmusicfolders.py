import xml.etree.ElementTree as ET

from . import Command, registerCmd
from ...models import Library


@registerCmd
class GetMusicFolders(Command):
    name = "getMusicFolders.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        folders = ET.Element("musicFolders")
        for row in session.query(Library).all():
            if row.name == "__null_lib__":
                continue
            folder = ET.Element("musicFolder")
            folders.append(folder)
            folder.set("id", "fl-%s" % row.id)
            folder.set("name", row.name)
        return self.makeResp(child=folders)
