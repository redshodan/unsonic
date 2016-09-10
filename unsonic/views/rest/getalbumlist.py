import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.sql.expression import func as dbfunc

from . import (Command, MissingParam, addCmd, fillAlbum, fillAlbumUser,
               fillArtist, fillSong)
from ...models import (Session, Artist, Album, AlbumRating, PlayCount, Track,
                       Scrobble)


class GetAlbumList(Command):
    name = "getAlbumList.view"
    param_defs = {
        "size": {"default": 10, "type": int},
        "offset": {"default": 0, "type": int},
        "type": {"required": True,
                 "values": ["alphabeticalByName", "alphabeticalByArtist",
                            "frequent", "highest", "newest", "random",
                            "recent", "starred",]},
        }
    dbsess = True


    def processRows(self, session, alist, result):
        for row in result:
            album = fillAlbumUser(session, row, self.req.authed_user)
            alist.append(album)
            if row.artist:
                album.set("parent", "ar-%d" % row.artist.id)
            else:
                album.set("parent", "UNKNOWN")
            album.set("title", album.get("name"))
            album.set("isDir", "true")


    def handleReq(self, session):
        alist = ET.Element("albumList")
        size = self.params["size"]
        offset = self.params["offset"]
        limit = offset + size
        if self.params["type"] == "random":
            result = session.query(Album). \
                         options(subqueryload("*")). \
                         order_by(dbfunc.random()). \
                         offset(offset). \
                         limit(limit)
            self.processRows(session, alist, result)
        elif self.params["type"] == "newest":
            result = session.query(Album). \
                         options(subqueryload("*")). \
                         order_by(Album.date_added). \
                         offset(offset). \
                         limit(limit)
            self.processRows(session, alist, result)
        elif self.params["type"] == "highest":
            result = session.query(AlbumRating). \
                        options(subqueryload("*")). \
                        filter(AlbumRating.user_id ==
                               self.req.authed_user.id). \
                         order_by(AlbumRating.rating). \
                         offset(offset). \
                         limit(limit)
            albums = []
            for arate in result:
                albums.append(arate.album)
            self.processRows(session, alist, albums)
        elif self.params["type"] == "frequent":
            pcounts = session.query(PlayCount). \
                         options(subqueryload("*")). \
                         join(Track). \
                         filter(PlayCount.user_id ==
                                self.req.authed_user.id). \
                         order_by(PlayCount.count). \
                         offset(offset). \
                         limit(limit)
            albums = []
            for pcount in pcounts:
                if not pcount.track.album:
                    continue
                if pcount.track.album not in albums:
                    albums.append(pcount.track.album)
                if len(albums) >= size:
                    break
            self.processRows(session, alist, albums)
        elif self.params["type"] == "recent":
            result = session.query(Scrobble). \
                        options(subqueryload("*")). \
                        filter(Scrobble.user_id ==
                               self.req.authed_user.id). \
                        order_by(Scrobble.tstamp.desc()). \
                        offset(offset). \
                        limit(limit)
            albums = []
            for scrobble in result:
                if not scrobble.track.album:
                    continue
                if scrobble.track.album not in albums:
                    albums.append(scrobble.track.album)
                if len(albums) >= size:
                    break
            self.processRows(session, alist, albums)
        elif self.params["type"] == "starred":
            result = session.query(AlbumRating). \
                         options(subqueryload("*")). \
                         filter(AlbumRating.user_id ==
                                self.req.authed_user.id). \
                         filter(AlbumRating.starred is not None). \
                         order_by(AlbumRating.starred). \
                         offset(offset). \
                         limit(limit)
            albums = []
            for arate in result:
                albums.append(arate.album)
            self.processRows(session, alist, albums)
        elif self.params["type"] == "alphabeticalByName":
            result = session.query(Album). \
                         options(subqueryload("*")). \
                         order_by(Album.title). \
                         offset(offset). \
                         limit(limit)
            self.processRows(session, alist, result)
        elif self.params["type"] == "alphabeticalByArtist":
            size = self.params["size"]
            artists = session.query(Artist). \
                          options(subqueryload("*")). \
                          order_by("name"). \
                          limit(limit)
            for artist in artists:
                albums = session.query(Album). \
                             options(subqueryload("*")). \
                             filter(Album.artist_id == artist.id). \
                             order_by(Album.title). \
                             offset(offset). \
                             limit(limit)
                self.processRows(session, alist, artist.albums)
        else:
            # FIXME: Implement the rest once play tracking is done
            raise MissingParam("Unsupported type")

        return self.makeResp(child=alist)


addCmd(GetAlbumList)
