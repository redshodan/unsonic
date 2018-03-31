import xml.etree.ElementTree as ET

from . import Command, registerCmd, fillArtist, folder_t
from .. import DEFAULT_IGNORED_ARTICLES
from ...models import Artist, Album


@registerCmd
class GetArtists(Command):
    name = "getArtists.view"
    param_defs = {"musicFolderId": {"type": folder_t}}
    dbsess = True


    def handleReq(self, session):
        artists = ET.Element("artists")
        artists.set("ignoredArticles", " ".join(DEFAULT_IGNORED_ARTICLES))
        index_group = None
        q = session.query(Artist)
        if self.params["musicFolderId"]:
            q = q.filter(Artist.lib_id == self.params["musicFolderId"])
        for row in q.order_by(Artist.sort_name).all():
            first = row.sort_name[0].upper()
            index = None
            if index_group != first:
                index_group = first
                index = ET.Element("index")
                artists.append(index)
                index.set("name", index_group)
            artist = fillArtist(session, row)
            if index is not None:
                index.append(artist)
        for index in artists:
            for artist in index:
                count = 0
                for album in session.query(Album).filter(
                        Album.artist_id == int(artist.get("id")[3:])).all():
                    count = count + 1
                artist.set("albumCount", str(count))
        return self.makeResp(child=artists)
