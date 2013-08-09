import time
from . import Command, addCmd, bool_t, fillArtist, fillAlbum, fillSong
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label


class Search2(Command):
    name = "search2.view"
    param_defs = {
        "query": {"required": True},
        "artistCount": {"default": 20, "type": int},
        "artistOffset": {"default": 0, "type": int},
        "albumCount": {"default": 20, "type": int},
        "albumOffset": {"default": 0, "type": int},
        "songCount": {"default": 20, "type": int},
        "songOffset": {"default": 0, "type": int},
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
            count = 0
            for row in session.query(Artist). \
                           filter(Artist.name.ilike(u"%%%s%%" % query)). \
                           limit(ar_count). \
                           offset(ar_off):
                count += 1
                if count >= ar_off:
                    artist = fillArtist(row)
                    result.append(artist)
        if al_count:
            count = 0
            for row in session.query(Album). \
                           filter(Album.title.ilike(u"%%%s%%" % query)). \
                           limit(al_count). \
                           offset(al_off):
                count += 1
                if count >= al_off:
                    album = fillAlbum(row)
                    result.append(album)
        if tr_count:
            count = 0
            for row in session.query(Track). \
                           filter(Track.title.ilike(u"%%%s%%" % query)). \
                           limit(tr_count). \
                           offset(tr_off):
                count += 1
                if count >= tr_off:
                    track = fillSong(row)
                    result.append(track)
        return self.makeResp(child=result)


addCmd(Search2)
