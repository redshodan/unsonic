import xml.etree.ElementTree as ET

from . import (Command, MissingParam, NotFound, addCmd, fillAlbumUser,
               fillSongUser)
from ...models import Session, Artist, Album, Track
from ... import mash


class GetMusicDirectory(Command):
    name = "getMusicDirectory.view"
    param_defs = {"id": {"required": True}}
    dbsess = True


    def __init__(self, req):
        super(GetMusicDirectory, self).__init__(req)
        self.setParams()


    def setParams(self, dir_param="directory", album_param="child",
                  track_param="child"):
        self.dir_param = dir_param
        self.album_param = album_param
        self.track_param = track_param


    def handleReq(self, session):
        directory = ET.Element(self.dir_param)
        if self.params["id"].startswith("fl-"):
            raise Exception("TOP LEVEL FOLDER")
        elif self.params["id"].startswith("ar-"):
            artist_id = int(self.params["id"][3:])
            # FIXME: Do we care about the top level directory hierarchy?
            directory.set(
                "parent",
                "fl-%s" % list(mash.getPaths(self.settings).keys())[0])
            directory.set("id", self.params["id"])
            artist_name = None
            # Gather albums
            for row in session.query(Album).filter(
                    Album.artist_id == artist_id).all():
                album = fillAlbumUser(row, self.req.authed_user,
                                      self.album_param)
                directory.append(album)
                if row.artist and row.artist.name:
                    artist_name = row.artist.name
            # Gather tracks with no album
            for row in session.query(Track).filter(
                    Track.album_id == None, Track.artist_id == artist_id).\
                    order_by(Track.track_num).all():
                song = fillSongUser(row, self.req.authed_user, self.track_param)
                directory.append(song)
            if not artist_name:
                rows = session.query(Artist).filter(Artist.id ==
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
            for row in session.query(Track).filter(
                    Track.album_id == album_id).order_by(Track.track_num).all():
                song = fillSongUser(row, self.req.authed_user, self.track_param)
                directory.append(song)
                if row.artist:
                    dir_parent = "al-%d" % row.id
                if row.album and row.album.title:
                    dir_name = row.album.title
            if song is None:
                raise NotFound(self.params["id"])
            if dir_parent:
                directory.set("parent", dir_parent)
            if dir_name:
                directory.set("name", dir_name)
            directory.set("id", self.params["id"])
        elif self.params["id"].startswith("tr-"):
            track_id = int(self.params["id"][3:])
            row = session.query(Track).filter(Track.id == track_id).one()
            if row is None:
                raise NotFound(self.params["id"])
            song = fillSongUser(row, self.req.authed_user, self.track_param)
            if row.album:
                directory.set("parent", "al-%d" % row.album.id)
                directory.set("name", row.album.title)
            elif row.artist:
                directory.set("parent", "ar-%d" % row.artist.id)
                directory.set("name", row.artist.name)
            if self.dir_param == "song":
                directory = song
            else:
                directory.append(song)
        else:
            raise MissingParam("Invalid value for 'id'")
        return self.makeResp(child=directory)


addCmd(GetMusicDirectory)
