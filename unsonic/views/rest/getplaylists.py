import xml.etree.ElementTree as ET

from . import Command, addCmd, fillPlayList, InternalError
from ...models import (getUserByName, Session, PlayList, PlayListTrack,
                       PlayListUser)


class GetPlayLists(Command):
    name = "getPlaylists.view"
    param_defs = {"username": {}}
    dbsess = True

    
    def handleReq(self, session):
        username = self.params["username"]
        if username:
            other_user = getUser(username)
            if not other_user:
                raise MissingParam("Invalid username")
        else:
            other_user = None

        playlists = ET.Element("playlists")
        for plrow in session.query(PlayList). \
                         filter(PlayList.user_id ==
                                self.req.authed_user.id).all():
            playlist = fillPlayList(session, plrow)
            playlists.append(playlist)

        return self.makeResp(child=playlists)


addCmd(GetPlayLists)
