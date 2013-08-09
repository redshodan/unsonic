import time
from . import (Command, addCmd, bool_t, positive_t, fillArtist, fillAlbum,
               fillSong)
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label


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
        }
    
    def handleReq(self):
        query = self.params["query"]
        ar_count = self.params["artistCount"]
        ar_off = self.params["artistOffset"]
        al_count = self.params["albumCount"]
        al_off = self.params["albumOffset"]
        tr_count = self.params["songCount"]
        tr_off = self.params["songOffset"]

        session = self.mash_db.Session()
        result = ET.Element("searchResult2")
        if ar_count:
            for row in session.query(Artist). \
                           filter(Artist.name.ilike(u"%%%s%%" % query)). \
                           limit(ar_count). \
                           offset(ar_off):
                artist = fillArtist(row)
                result.append(artist)
        if al_count:
            for row in session.query(Album). \
                           filter(Album.title.ilike(u"%%%s%%" % query)). \
                           limit(al_count). \
                           offset(al_off):
                album = fillAlbum(row)
                result.append(album)
                if row.artist:
                    album.set("parent", "ar-%d" % row.artist.id)
                else:
                    album.set("parent", "UNKNOWN")
                album.set("isDir", "true")
                album.set("title", album.get("name"))
        if tr_count:
            for row in session.query(Track). \
                           filter(Track.title.ilike(u"%%%s%%" % query)). \
                           limit(tr_count). \
                           offset(tr_off):
                track = fillSong(row)
                result.append(track)
        return self.makeResp(child=result)


addCmd(Search2)
