import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import Command, addCmd, fillArtistUser
from ...models import Session, Artist, Album, Meta


class GetIndexes(Command):
    name = "getIndexes.view"
    param_defs = {
        "musicFolderId": {},
        "ifModifiedSince": {"type": int},
        }
    dbsess = True

    
    def handleReq(self, session):
        # TODO: handle params
        indexes = ET.Element("indexes")
        index_group = None
        for row in session.query(Meta):
            indexes.set("lastModified",
                        str(int(row.last_sync.timestamp() * 1000)))
            break
        rows = session.query(Artist).options(subqueryload("*")).\
            options(subqueryload("*")).order_by(Artist.sort_name).all()
        for row in rows:
            first = row.sort_name[0].upper()
            if index_group != first:
                index_group = first
                index = ET.Element("index")
                indexes.append(index)
                index.set("name", index_group)
            artist = fillArtistUser(session, row, None, self.req.authed_user)
            index.append(artist)
        for index in indexes:
            for artist in index:
                count = 0
                artist_id = int(artist.get("id")[3:])
                for album in session.query(Album).options(subqueryload("*")).\
                    filter(Album.artist_id == artist_id).all():
                    count = count + 1
                artist.set("albumCount", str(count))
        return self.makeResp(child=indexes)


addCmd(GetIndexes)
