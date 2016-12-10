import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload

from . import Command, addCmd, fillPlayList, InternalError, NoPerm
from ...models import Session, PlayList, PlayListTrack, PlayListUser


class GetPlayLists(Command):
    name = "getPlaylists.view"
    param_defs = {"username": {}}
    dbsess = True

    
    def handleReq(self, session):
        if (not self.params["username"] or
            self.req.authed_user.name == self.params["username"]):
            db_user = self.req.authed_user
        elif self.req.authed_user.isAdmin():
            db_user = getUserByName(session, self.params["username"])
        else:
            raise NoPerm("Can not view another user's playlists unless you "
                         "are an admin")

        playlists = ET.Element("playlists")
        for plrow in session.query(PlayList).options(subqueryload("*")). \
                             filter(PlayList.user_id == db_user.id).all():
            playlist = fillPlayList(session, plrow)
            playlists.append(playlist)

        return self.makeResp(child=playlists)


addCmd(GetPlayLists)
