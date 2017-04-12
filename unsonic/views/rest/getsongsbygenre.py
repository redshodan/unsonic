import xml.etree.ElementTree as ET

from sqlalchemy import and_
from sqlalchemy.sql.expression import func as dbfunc

from . import Command, registerCmd, fillTrackUser, folder_t, str_t, int_t
from ...models import Track, Tag, track_tags


@registerCmd
class GetSongsByGenre(Command):
    name = "getSongsByGenre.view"
    param_defs = {
        "genre": {"required": True, "type": str_t},
        "count": {"default": 10, "type": int_t},
        "offset": {"default": 0, "type": int_t},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True


    def handleReq(self, session):
        songs = ET.Element("songsByGenre")
        genre = self.params["genre"]
        count = self.params["count"]
        offset = self.params["offset"]
        limit = offset + count
        if self.params["musicFolderId"]:
            lib_id = self.params["musicFolderId"]
        else:
            lib_id = None

        # TODO: When mishmash does album tags/genres, do that too
        # TODO: Cache tags?
        tag = session.query(Tag).\
            filter(dbfunc.lower(Tag.name) == genre.lower()).one_or_none()
        if not tag:
            return self.makeResp(child=songs)
        q = session.query(Track).\
            join(track_tags).\
            filter(and_(Track.id == track_tags.c.track_id,
                        track_tags.c.tag_id == tag.id))
        if lib_id:
            q = q.filter(Track.lib_id == lib_id)
        result = q.order_by(Track.title).\
            offset(offset).\
            limit(limit)
        for row in result:
            song = fillTrackUser(session, row, None, self.req.authed_user,
                                 "song")
            songs.append(song)
            if row.album:
                song.set("parent", "al-%d" % row.album.id)
            else:
                song.set("parent", "UNKNOWN")

        return self.makeResp(child=songs)
