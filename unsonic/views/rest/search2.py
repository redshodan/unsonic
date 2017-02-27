import xml.etree.ElementTree as ET

from . import (Command, registerCmd, positive_t, fillArtist, fillAlbum,
               fillTrack, folder_t)
from ...models import Artist, Album, Track


@registerCmd
class Search2(Command):
    name = "search2.view"
    param_defs = {
        "query": {"required": True},
        "artistCount": {"default": 20, "type": positive_t},
        "artistOffset": {"default": 0, "type": positive_t},
        "albumCount": {"default": 20, "type": positive_t},
        "albumOffset": {"default": 0, "type": positive_t},
        "songCount": {"default": 20, "type": positive_t},
        "songOffset": {"default": 0, "type": positive_t},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True


    def query(self, session, klass):
        if self.params["musicFolderId"]:
            return (session.query(klass).
                    filter(klass.lib_id == self.params["musicFolderId"]))
        else:
            return session.query(klass)


    def handleReq(self, session):
        query = self.params["query"]
        ar_count = self.params["artistCount"]
        ar_off = self.params["artistOffset"]
        al_count = self.params["albumCount"]
        al_off = self.params["albumOffset"]
        tr_count = self.params["songCount"]
        tr_off = self.params["songOffset"]

        result = ET.Element("searchResult2")
        if ar_count:
            for row in self.query(session, Artist). \
                           filter(Artist.name.ilike("%%%s%%" % query)). \
                           limit(ar_count). \
                           offset(ar_off):
                artist = fillArtist(session, row)
                result.append(artist)
        if al_count:
            for row in self.query(session, Album). \
                           filter(Album.title.ilike("%%%s%%" % query)). \
                           limit(al_count). \
                           offset(al_off):
                album = fillAlbum(session, row)
                result.append(album)
        if tr_count:
            for row in self.query(session, Track). \
                           filter(Track.title.ilike("%%%s%%" % query)). \
                           limit(tr_count). \
                           offset(tr_off):
                track = fillTrack(session, row)
                result.append(track)
        return self.makeResp(child=result)
