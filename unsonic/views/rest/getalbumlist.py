from . import Command, MissingParam, addCmd, fillAlbum, fillArtist, fillSong
import xml.etree.ElementTree as ET
from  sqlalchemy.sql.expression import func as dbfunc

from mishmash.orm import Track, Artist, Album, Meta, Label

from ... import db


class GetAlbumList(Command):
    def __init__(self):
        super(GetAlbumList, self).__init__("getAlbumList")
        
    def handleReq(self, req):
        # Param handling
        size, offset, album_type = \
          self.getParams(req, (("size", 10), ("offset", 0)), (("type", None),))
        size = int(size)
        offset = int(offset)
        if album_type not in ["random", "newest", "highest", "frequent",
                              "recent", "starred", "alphabeticalByName",
                              "alphabeticalByArtist"]:
            raise MissingParam("Invalid type")
        
        # Processing
        alist = ET.Element("albumList")
        session = self.mash_db.Session()
        if album_type == "random":
            result = session.query(Album).order_by(dbfunc.random()).limit(size)
        elif album_type == "newest":
            result = session.query(Album).order_by(Album.date_added).limit(size)
        elif album_type == "alphabeticalByName":
            result = session.query(Album).order_by(Album.title).limit(size)
        # elif album_type == "alphabeticalByArtist":
        # FIXME: How to do this with sqlalchemy?
        #result=session.query(Album).order_by(Album.artist.name).limit(size)
        else:
            # FIXME: Implement the rest once play tracking is done
            raise MissingParam("Unsupported type")

        count = 0
        for row in result:
            count += 1
            if count <= offset:
                continue
            album = fillAlbum(row)
            alist.append(album)
            if row.artist:
                album.set("parent", "ar-%d" % row.artist.id)
            else:
                album.set("parent", "UNKNOWN")
            album.set("title", album.get("name"))
            album.set("isDir", "true")
        return self.makeResp(req, child=alist)


addCmd(GetAlbumList())
