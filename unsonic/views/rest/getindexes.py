from . import Command, addCmd, fillArtist
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetIndexes(Command):
    def __init__(self):
        super(GetIndexes, self).__init__("getIndexes")
        self.param_defs = {"id": {}}
        
    def handleReq(self, req):
        # TODO: handle param id
        session = self.mash_db.Session()
        indexes = ET.Element("indexes")
        index_group = None
        for row in session.query(Artist).order_by(Artist.sort_name).all():
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
                for album in session.query(Album).filter(
                        Album.artist_id == artist_id).all():
                    count = count + 1
                artist.set("albumCount", str(count))
        return self.makeResp(req, child=indexes)


addCmd(GetIndexes())
