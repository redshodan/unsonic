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

        q = session.query(Artist)
        if self.params["musicFolderId"]:
            q = q.filter(Artist.lib_id == self.params["musicFolderId"])
        indexes = {}
        for row in q.all():
            first = row.sort_name[0].upper()
            if first in indexes:
                index = indexes[first]
            else:
                index = []
                indexes[first] = index
            count = 0
            for album in session.query(Album).filter(
                    Album.artist_id == row.id).all():
                count = count + 1
            artist = fillArtist(session, row)
            artist.set("albumCount", str(count))
            index.append(artist)

        for key in sorted(indexes.keys()):
            val = indexes[key]
            index = ET.Element("index")
            index.set("name", key)
            for artist in val:
                index.append(artist)
            artists.append(index)

        return self.makeResp(child=artists)
