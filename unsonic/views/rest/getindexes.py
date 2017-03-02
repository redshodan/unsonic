from datetime import datetime
import xml.etree.ElementTree as ET

from . import Command, registerCmd, fillArtistUser, folder_t, datetime_t
from ...models import Artist, Meta


@registerCmd
class GetIndexes(Command):
    name = "getIndexes.view"
    param_defs = {
        "musicFolderId": {"type": folder_t},
        "ifModifiedSince": {"type": datetime_t},
        }
    dbsess = True


    def handleReq(self, session):
        indexes = ET.Element("indexes")
        index_group = None
        row = session.query(Meta).one_or_none()

        # Return empty response if sync is older
        if (self.params["ifModifiedSince"] and
                (self.params["ifModifiedSince"] >=
                 datetime.utcfromtimestamp(row.last_sync.timestamp()))):
            return self.makeResp()

        # TODO: Use libraries.last_sync once its done in mishmash
        indexes.set("lastModified",
                    str(int(row.last_sync.timestamp() * 1000)))
        # TODO: find the actual ignored articles
        indexes.set("ignoredArticles", "")

        q = session.query(Artist)
        if self.params["musicFolderId"]:
            q = q.filter(Artist.lib_id == self.params["musicFolderId"])
        rows = q.order_by(Artist.sort_name).all()
        for row in rows:
            first = row.sort_name[0].upper()
            if index_group != first:
                index_group = first
                index = ET.Element("index")
                indexes.append(index)
                index.set("name", index_group)
            artist = fillArtistUser(session, row, None, self.req.authed_user)
            index.append(artist)
        return self.makeResp(child=indexes)
