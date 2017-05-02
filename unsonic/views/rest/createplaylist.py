from . import Command, registerCmd, MissingParam, track_t, playlist_t
from .getplaylist import GetPlayList
from ...models import PlayList, PlayListTrack, Track


@registerCmd
class CreatePlayList(Command):
    name = "createPlaylist.view"
    param_defs = {
        "playlistId": {"type": playlist_t},
        "name": {},
        "songId": {"multi": True, "type": track_t},
        }
    dbsess = True


    def handleReq(self, session):
        plid = self.params["playlistId"]
        if plid and self.params["name"]:
            raise MissingParam(
                "Can't supply playlistId and name at the same time")
        elif (not plid and not self.params["name"]):
            raise MissingParam("Must supply playlistId or name")

        if plid:
            # Update/append case
            plist = session.query(PlayList).filter(
                PlayList.id == plid).one_or_none()
            if plist is None:
                raise MissingParam("Invalid playlistId: pl-%s" % plid)
        else:
            # New creation case
            plist = PlayList(user_id=self.req.authed_user.id,
                             name=self.params["name"])
            session.add(plist)

        # Add tracks
        for sid in self.params["songId"]:
            track = session.query(Track).filter(Track.id == sid).one_or_none()
            if track is None:
                raise MissingParam("Invalid songId: tr-%s" % sid)
            pltrack = PlayListTrack(track_id=track.id, playlist_id=plist.id)
            session.add(pltrack)

        session.flush()

        # Fun little hack to return the newly created playlist
        self.params["id"] = plist.id
        return GetPlayList.handleReq(self, session)
