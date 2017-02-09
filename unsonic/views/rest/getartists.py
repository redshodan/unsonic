import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import Command, addCmd, fillArtist
from ...models import Artist, Album


class GetArtists(Command):
    name = "getArtists.view"
    param_defs = {"musicFolderId": {}}
    dbsess = True


    def handleReq(self, session):
        artists = ET.Element("artists")
        # TODO: find the actual ignored articles
        artists.set("ignoredArticles", "")
        index_group = None
        for row in session.query(Artist).options(subqueryload("*")). \
          order_by(Artist.sort_name).all():
            first = row.sort_name[0].upper()
            if index_group != first:
                index_group = first
                index = ET.Element("index")
                artists.append(index)
                index.set("name", index_group)
            artist = fillArtist(session, row)
            index.append(artist)
        for index in artists:
            for artist in index:
                count = 0
                for album in session.query(Album).options(subqueryload("*")). \
                  filter(Album.artist_id == int(artist.get("id")[3:])).all():
                    count = count + 1
                artist.set("albumCount", str(count))
        return self.makeResp(child=artists)


addCmd(GetArtists)
