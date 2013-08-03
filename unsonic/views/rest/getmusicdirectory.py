from . import Command, MissingParam, addCmd, fillAlbum, fillArtist, fillSong
import xml.etree.ElementTree as ET

from mishmash.orm import Track, Artist, Album, Meta, Label

from ... import db


class GetMusicDirectory(Command):
    def __init__(self):
        super(GetMusicDirectory, self).__init__("getMusicDirectory")
        self.param_defs = {"id": {"required": True}}
        
    def handleReq(self, req):
        session = self.mash_db.Session()
        directory = ET.Element("directory")
        if self.params["id"].startswith("fl-"):
            raise Exception("TOP LEVEL FOLDER")
        elif self.params["id"].startswith("ar-"):
            artist_id = int(self.params["id"][3:])
            # FIXME: Do we care about the top level directory hierarchy?
            directory.set("parent", db.getMashPaths(self.mash_settings).keys()[0])
            directory.set("id", self.params["id"])
            artist_name = "UNKNOWN"
            for row in session.query(Album).filter(
                    Album.artist_id == artist_id).all():
                album = ET.Element("child")
                directory.append(album)
                album.set("id", "al-%d" % row.id)
                album.set("parent", self.params["id"])
                album.set("title", row.title)
                if row.artist and row.artist.name:
                    artist_name = row.artist.name
                    album.set("artist", row.artist.name)
                album.set("isDir", "true")
                album.set("coverArt", "al-%d" % row.id)
            directory.set("name", artist_name)
        elif self.params["id"].startswith("al-"):
            album_id = int(self.params["id"][3:])
            dir_parent = "-1"
            dir_name = "UNKNOWN"
            for row in session.query(Track).filter(Track.album_id == album_id).all():
                song = fillSong(row, "child")
                directory.append(song)
                if row.artist:
                    dir_parent = "al-%d" % row.artist.id
                if row.album and row.album.title:
                    dir_name = row.album.title
            directory.set("parent", dir_parent)
            directory.set("id", self.params["id"])
        else:
            raise MissingParam("Invalid value for 'id'")
        return self.makeResp(req, child=directory)


addCmd(GetMusicDirectory())
