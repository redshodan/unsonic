import xml.etree.ElementTree as ET

from . import Command, addCmd, fillPlayList, InternalError
from ...models import (getUserByName, DBSession, PlayList, PlayListTrack,
                       PlayListUser)


class GetPlayLists(Command):
    name = "getPlaylists.view"
    param_defs = {"username": {}}
    
    def handleReq(self):
        username = self.params["username"]
        if username:
            other_user = getUser(username)
            if not other_user:
                raise MissingParam("Invalid username")
        else:
            other_user = None

        playlists = ET.Element("playlists")
        for plrow in DBSession.query(PlayList). \
                         filter(PlayList.owner_id ==
                                self.req.authed_user.id).all():
            playlist = fillPlayList(plrow)
            playlists.append(playlist)

        return self.makeResp(child=playlists)


addCmd(GetPlayLists)
