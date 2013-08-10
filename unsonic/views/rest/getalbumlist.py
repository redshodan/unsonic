from . import Command, MissingParam, addCmd, fillAlbum, fillArtist, fillSong
import xml.etree.ElementTree as ET
from  sqlalchemy.sql.expression import func as dbfunc

from mishmash.orm import Track, Artist, Album, Meta, Label


class GetAlbumList(Command):
    name = "getAlbumList.view"
    param_defs = {
        "size": {"default": 10, "type": int},
        "offset": {"default": 0, "type": int},
        "type": {"required": True,
                 "values": ["random", "newest", "highest", "frequent",
                            "recent", "starred", "alphabeticalByName",
                            "alphabeticalByArtist"]},
        }
    
    def handleReq(self):
        alist = ET.Element("albumList")
        session = self.mash_db.Session()
        if self.params["type"] == "random":
            result = session.query(Album).order_by(dbfunc.random()). \
                         limit(self.params["size"])
        elif self.params["type"] == "newest":
            result = session.query(Album).order_by(Album.date_added). \
                         limit(self.params["size"])
        elif self.params["type"] == "alphabeticalByName":
            result = session.query(Album).order_by(Album.title). \
                         limit(self.params["size"])
        # elif self.params["type"] == "alphabeticalByArtist":
        # FIXME: How to do this with sqlalchemy?
        #result=session.query(Album).order_by(Album.artist.name).limit(size)
        else:
            # FIXME: Implement the rest once play tracking is done
            raise MissingParam("Unsupported type")

        count = 0
        for row in result:
            count += 1
            if count <= self.params["offset"]:
                continue
            album = fillAlbum(row)
            alist.append(album)
            if row.artist:
                album.set("parent", "ar-%d" % row.artist.id)
            else:
                album.set("parent", "UNKNOWN")
            album.set("title", album.get("name"))
            album.set("isDir", "true")
        return self.makeResp(child=alist)


addCmd(GetAlbumList)
