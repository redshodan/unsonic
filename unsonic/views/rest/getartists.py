from . import Command, addCmd, fillArtist
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetArtists(Command):
    def __init__(self):
        super(GetArtists, self).__init__("getArtists")
        
    def handleReq(self, req):
        # Processing
        session = self.mash_db.Session()
        artists = ET.Element("artists")
        index_group = None
        for row in session.query(Artist).order_by(Artist.sort_name).all():
            first = row.sort_name[0].upper()
            if index_group != first:
                index_group = first
                index = ET.Element("index")
                artists.append(index)
                index.set("name", index_group)
            artist = fillArtist(row)
            index.append(artist)
        for index in artists:
            for artist in index:
                count = 0
                for album in session.query(Album).filter(
                        Album.artist_id == int(artist.get("id"))).all():
                    count = count + 1
                artist.set("albumCount", str(count))
        return self.makeResp(req, child=artists)


addCmd(GetArtists())
