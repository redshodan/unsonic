from . import (Command, registerCmd, fillPlayList, fillTrack, playlist_t,
               MissingParam)
from ...models import PlayList


@registerCmd
class GetPlayList(Command):
    name = "getPlaylist.view"
    param_defs = {"id": {"required": True, "type": playlist_t}}
    dbsess = True


    def handleReq(self, session):
        plrow = session.query(PlayList). \
                    filter(PlayList.id == self.params["id"]). \
                    filter(PlayList.user_id == self.req.authed_user.id). \
                    one_or_none()
        if not plrow:
            raise MissingParam("Invalid playlist id: %s" % self.params["id"])

        playlist = fillPlayList(session, plrow)
        for pltrack in plrow.tracks:
            entry = fillTrack(session, pltrack.track, name="entry")
            playlist.append(entry)

        return self.makeResp(child=playlist)
