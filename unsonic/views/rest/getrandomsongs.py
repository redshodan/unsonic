import xml.etree.ElementTree as ET

from sqlalchemy import and_
from sqlalchemy.sql.expression import func as dbfunc

from . import Command, registerCmd, fillTrack, year_t, folder_t, int_t, str_t
from ...models import Album, Track, Tag, track_tags


@registerCmd
class GetRandomSongs(Command):
    name = "getRandomSongs.view"
    param_defs = {
        "size": {"default": 10, "type": int_t},
        "genre": {"type": str_t},
        "fromYear": {"type": year_t},
        "toYear": {"type": year_t},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True


    def query(self, session):
        if self.params["musicFolderId"]:
            return (session.query(Track).
                    filter(Track.lib_id == self.params["musicFolderId"]))
        else:
            return session.query(Track)


    def handleReq(self, session):
        random_songs = ET.Element("randomSongs")
        genre = self.params["genre"]
        fy = self.params["fromYear"]
        ty = self.params["toYear"]
        if genre:
            tag = session.query(Tag).\
                filter(dbfunc.lower(Tag.name) == genre.lower()).one_or_none()
            if not tag:
                return self.makeResp(child=random_songs)
            rows = (self.query(session).join(track_tags).
                    filter(and_(Track.id == track_tags.c.track_id,
                                track_tags.c.tag_id == tag.id)).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif fy and ty:
            rows = (self.query(session).
                    join(Album).filter(Album.release_date >= fy and
                                       Album.release_date <= ty).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif fy:
            rows = (self.query(session).
                    join(Album).filter(Album.release_date >= fy).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        elif ty:
            rows = (self.query(session).
                    join(Album).filter(Album.release_date <= ty).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        else:
            rows = (self.query(session).
                    order_by(dbfunc.random()).limit(self.params["size"]))
        for row in rows:
            song = fillTrack(session, row)
            random_songs.append(song)
        return self.makeResp(child=random_songs)
