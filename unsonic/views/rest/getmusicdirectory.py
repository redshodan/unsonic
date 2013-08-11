import xml.etree.ElementTree as ET

from . import (Command, MissingParam, NotFound, addCmd, fillAlbum, fillArtist,
               fillSong)
from ...models import DBSession, Artist, Album, Track
from ... import mash


class GetMusicDirectory(Command):
    name = "getMusicDirectory.view"
    param_defs = {"id": {"required": True}}

    def handleReq(self):
        directory = ET.Element("directory")
        if self.params["id"].startswith("fl-"):
            raise Exception("TOP LEVEL FOLDER")
        elif self.params["id"].startswith("ar-"):
            artist_id = int(self.params["id"][3:])
            # FIXME: Do we care about the top level directory hierarchy?
            directory.set(
                "parent",
                "fl-%s" % mash.getPaths(self.settings).keys()[0])
            directory.set("id", self.params["id"])
            artist_name = None
            for row in DBSession.query(Album).filter(
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
            if not artist_name:
                rows = DBSession.query(Artist).filter(Artist.id ==
                                                      artist_id).all()
                if len(rows) == 1:
                    artist_name = rows[0].name
            if not artist_name:
                raise NotFound(self.params["id"])
            directory.set("name", artist_name)
        elif self.params["id"].startswith("al-"):
            album_id = int(self.params["id"][3:])
            dir_parent = None
            dir_name = None
            song = None
            for row in DBSession.query(Track).filter(Track.album_id ==
                                                     album_id).all():
                song = fillSong(row, "child")
                directory.append(song)
                if row.artist:
                    dir_parent = "ar-%d" % row.artist.id
                if row.album and row.album.title:
                    dir_name = row.album.title
            if song is None:
                raise NotFound(self.params["id"])
            if dir_parent:
                directory.set("parent", dir_parent)
            if dir_name:
                directory.set("name", dir_name)
            directory.set("id", self.params["id"])
        else:
            raise MissingParam("Invalid value for 'id'")
        return self.makeResp(child=directory)


addCmd(GetMusicDirectory)
