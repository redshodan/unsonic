from . import Command, registerCmd, playlist_t, MissingParam
from ...models import PlayList


@registerCmd
class DeletePlayList(Command):
    name = "deletePlaylist.view"
    param_defs = {"id": {"required": True, "type": playlist_t}}
    dbsess = True


    def handleReq(self, session):
        res = session.query(PlayList). \
                    filter(PlayList.id == self.params["id"]). \
                    filter(PlayList.user_id == self.req.authed_user.id)
        if not res.one_or_none():
            raise MissingParam("Invalid playlist id: %s" % self.params["id"])
        res.delete()

        return self.makeResp()
