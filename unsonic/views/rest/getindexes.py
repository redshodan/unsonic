import xml.etree.ElementTree as ET

from . import Command, addCmd, fillArtist
from ...models import DBSession, Artist, Album


class GetIndexes(Command):
    name = "getIndexes.view"
    param_defs = {
        "musicFolderId": {},
        "ifModifiedSince": {},
        }
        
    def handleReq(self):
        # TODO: handle params
        indexes = ET.Element("indexes")
        index_group = None
        for row in DBSession.query(Artist).order_by(Artist.sort_name).all():
            first = row.sort_name[0].upper()
            if index_group != first:
                index_group = first
                index = ET.Element("index")
                indexes.append(index)
                index.set("name", index_group)
            artist = fillArtist(row)
            index.append(artist)
        for index in indexes:
            for artist in index:
                count = 0
                artist_id = int(artist.get("id")[3:])
                for album in DBSession.query(Album).filter(
                        Album.artist_id == artist_id).all():
                    count = count + 1
                artist.set("albumCount", str(count))
        return self.makeResp(child=indexes)


addCmd(GetIndexes)
