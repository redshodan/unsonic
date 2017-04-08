import xml.etree.ElementTree as ET

from . import (Command, registerCmd, MissingParam, NotFound, fillAlbumUser,
               fillTrackUser)
from ...models import Artist, Album, Track


@registerCmd
class GetMusicDirectory(Command):
    name = "getMusicDirectory.view"
    param_defs = {"id": {"required": True}}
    dbsess = True


    def __init__(self, route, req, session=None):
        super(GetMusicDirectory, self).__init__(route, req, session)
        self.setParams()


    def setParams(self, dir_param="directory", album_param="child",
                  track_param="child"):
        self.dir_param = dir_param
        self.album_param = album_param
        self.track_param = track_param


    def handleReq(self, session):
        directory = ET.Element(self.dir_param)
        directory.set("id", self.params["id"])
        # FIXME: Do we care about the top level directory hierarchy?
        if self.params["id"].startswith("fl-"):
            raise Exception("TOP LEVEL FOLDER")
        elif self.params["id"].startswith("ar-"):
            artist_id = int(self.params["id"][3:])
            row = session.query(Artist).filter(
                Artist.id == artist_id).one_or_none()
            if row:
                directory.set("name", row.name)
                directory.set("parent", "fl-%s" % row.lib_id)
            else:
                raise NotFound(self.params["id"])
            # Gather albums
            for row in session.query(Album).filter(
                    Album.artist_id == artist_id).all():
                album = fillAlbumUser(session, row, None, self.req.authed_user,
                                      self.album_param)
                directory.append(album)
            # Gather tracks with no album
            for row in session.query(Track).filter(
                    Track.album_id is None, Track.artist_id == artist_id).\
                    order_by(Track.track_num).all():
                song = fillTrackUser(session, row, None, self.req.authed_user,
                                     self.track_param)
                directory.append(song)
        elif self.params["id"].startswith("al-"):
            album_id = int(self.params["id"][3:])
            album = session.query(Album).filter(
                Album.id == album_id).one_or_none()
            if not album:
                raise NotFound(self.params["id"])
            directory.set("parent", "ar-%d" % album.artist_id)
            directory.set("name", album.title)
            directory.set("id", self.params["id"])
            song = None
            for row in session.query(Track).filter(
                    Track.album_id == album_id).order_by(Track.track_num).all():
                song = fillTrackUser(session, row, None, self.req.authed_user,
                                     self.track_param)
                directory.append(song)
            if song is None:
                raise NotFound(self.params["id"])
        elif self.params["id"].startswith("tr-"):
            track_id = int(self.params["id"][3:])
            row = session.query(Track).filter(Track.id == track_id).one()
            if row is None:
                raise NotFound(self.params["id"])
            song = fillTrackUser(session, row, None, self.req.authed_user,
                                 self.track_param)
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
