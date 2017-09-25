import xml.etree.ElementTree as ET

from sqlalchemy.sql.expression import func as dbfunc

from eyed3.core import Date as Eyed3Date

from . import (Command, registerCmd, MissingParam, fillAlbumUser, folder_t,
               str_t, int_t)
from ...models import (Artist, Album, AlbumRating, PlayCount, Track,
                       Scrobble, Tag, track_tags)


@registerCmd
class GetAlbumList(Command):
    name = "getAlbumList.view"
    param_defs = {
        "size": {"default": 10, "type": int_t},
        "offset": {"default": 0, "type": int_t},
        "fromYear": {"type": int_t},
        "toYear": {"type": int_t},
        "genre": {"type": str_t},
        "type": {"required": True,
                 "values": ["alphabeticalByName", "alphabeticalByArtist",
                            "frequent", "highest", "newest", "random",
                            "recent", "starred", "byYear", "byGenre"]},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True

    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        self.setParams()


    def setParams(self, list_param="albumList"):
        self.list_param = list_param


    def processRows(self, session, alist, result):
        for row in result:
            album = fillAlbumUser(session, row, None, self.req.authed_user)
            alist.append(album)
            if row.artist:
                album.set("parent", "ar-%d" % row.artist.id)
            else:
                album.set("parent", "UNKNOWN")


    def queryAlbum(self, session):
        if self.params["musicFolderId"]:
            return (session.query(Album).
                    filter(Album.lib_id == self.params["musicFolderId"]))
        else:
            return session.query(Album)


    def handleReq(self, session):
        if self.params["musicFolderId"]:
            lib_id = self.params["musicFolderId"]
        else:
            lib_id = None
        alist = ET.Element(self.list_param)
        size = self.params["size"]
        offset = self.params["offset"]
        limit = offset + size
        if self.params["type"] == "random":
            result = self.queryAlbum(session).\
                         order_by(dbfunc.random()).\
                         offset(offset).\
                         limit(limit)
            self.processRows(session, alist, result)
        elif self.params["type"] == "newest":
            from sqlalchemy import desc as desc_
            albums = session.query(Album)\
                            .order_by(desc_("date_added"))\
                            .offset(offset).limit(limit).all()
            # FIXME: handle new singles here, make sure this works for various
            self.processRows(session, alist, albums)
        elif self.params["type"] == "highest":
            result = session.query(AlbumRating). \
                         filter(AlbumRating.user_id ==
                                self.req.authed_user.id). \
                         order_by(AlbumRating.rating). \
                         offset(offset). \
                         limit(limit)
            albums = []
            for arate in result:
                # TODO: Replace this with the correct sqlalchemy magic
                if lib_id is None or arate.album.lib_id == lib_id:
                    albums.append(arate.album)
            self.processRows(session, alist, albums)
        elif self.params["type"] == "frequent":
            pcounts = session.query(PlayCount).\
                         join(Track).\
                         filter(PlayCount.user_id ==
                                self.req.authed_user.id).\
                         order_by(PlayCount.count).\
                         offset(offset).\
                         limit(limit)
            albums = []
            for pcount in pcounts:
                if not pcount.track.album:
                    continue
                # TODO: Replace this with the correct sqlalchemy magic
                if lib_id and pcount.track.lib_id != lib_id:
                    continue
                if pcount.track.album not in albums:
                    albums.append(pcount.track.album)
                if len(albums) >= size:
                    break
            self.processRows(session, alist, albums)
        elif self.params["type"] == "recent":
            result = session.query(Scrobble).\
                        filter(Scrobble.user_id ==
                               self.req.authed_user.id).\
                        order_by(Scrobble.tstamp.desc()).\
                        offset(offset).\
                        limit(limit)
            albums = []
            for scrobble in result:
                if not scrobble.track.album:
                    continue
                # TODO: Replace this with the correct sqlalchemy magic
                if lib_id and scrobble.track.lib_id != lib_id:
                    continue
                if scrobble.track.album not in albums:
                    albums.append(scrobble.track.album)
                if len(albums) >= size:
                    break
            self.processRows(session, alist, albums)
        elif self.params["type"] == "starred":
            result = session.query(AlbumRating).\
                         filter(AlbumRating.user_id ==
                                self.req.authed_user.id).\
                         filter(AlbumRating.starred is not None).\
                         order_by(AlbumRating.starred).\
                         offset(offset).\
                         limit(limit)
            albums = []
            for arate in result:
                # TODO: Replace this with the correct sqlalchemy magic
                if lib_id is None or arate.album.lib_id != lib_id:
                    albums.append(arate.album)
            self.processRows(session, alist, albums)
        elif self.params["type"] == "alphabeticalByName":
            result = self.queryAlbum(session).\
                         order_by(Album.title).\
                         offset(offset).\
                         limit(limit)
            self.processRows(session, alist, result)
        elif self.params["type"] == "alphabeticalByArtist":
            artists = session.query(Artist).\
                          order_by("name").\
                          limit(limit)
            for artist in artists:
                albums = self.queryAlbum(session).\
                             filter(Album.artist_id == artist.id).\
                             order_by(Album.title).\
                             offset(offset).\
                             limit(limit)
                self.processRows(session, alist, artist.albums)
        elif self.params["type"] == "byYear":
            to_year = self.params["toYear"]
            from_year = self.params["fromYear"]
            if not to_year or not from_year:
                raise MissingParam("Missing proper toYear/fromYear parameters "
                                   "for search byYear")
            if from_year > to_year:
                desc = True
                to_year = Eyed3Date(year=from_year, month=12, day=31)
                from_year = Eyed3Date(year=to_year, month=1, day=1)
            else:
                desc = False
                from_year = Eyed3Date(year=from_year, month=1, day=1)
                to_year = Eyed3Date(year=to_year, month=12, day=31)
            results = set()
            second = False
            for date_row in [Album.original_release_date, Album.release_date,
                             Album.recording_date]:
                res = self.queryAlbum(session).\
                          filter(date_row >= from_year, date_row <= to_year).\
                          offset(offset).\
                          limit(limit)
                if not second:
                    second = True
                    for row in res.all():
                        results.add(row)
                else:
                    for row in res.all():
                        # If no orig date, go ahead and add it
                        if not row.original_release_date:
                            results.add(row)
                        # Add only if the orig date is in the range and ignore
                        # rel date
                        elif ((row.original_release_date >= from_year) and
                              (row.original_release_date <= to_year)):
                            results.add(row)
            results = list(results)
            results.sort(key=lambda x: x.getBestDate(), reverse=desc)
            self.processRows(session, alist, results)
        elif self.params["type"] == "byGenre":
            genre = self.params["genre"]
            if not genre:
                raise MissingParam("Missing genre param when searching byGenre")

            tag = session.query(Tag).\
                filter(dbfunc.lower(Tag.name) == genre.lower()).one_or_none()
            if not tag:
                return self.makeResp(child=alist)

            result = session.query(Album).\
                join(Track).\
                join(track_tags).\
                filter(Album.id == Track.album_id,
                       Track.id == track_tags.c.track_id,
                       track_tags.c.tag_id == tag.id).\
                group_by(Album).\
                order_by(Album.title).\
                offset(offset).\
                limit(limit)
            self.processRows(session, alist, result)
        else:
            raise MissingParam("Unsupported type")

        return self.makeResp(child=alist)
