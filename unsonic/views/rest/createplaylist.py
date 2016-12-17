import xml.etree.ElementTree as ET

from . import Command, addCmd, InternalError, MissingParam, track_t, playlist_t
from .getplaylist import GetPlayList
from ...models import Session, PlayList, PlayListTrack, Track


class CreatePlayList(Command):
    name = "createPlaylist.view"
    param_defs = {
        "playlistId": {"type": playlist_t},
        "name": {},
        "songId": {"multi": True, "type": track_t},
        }
    dbsess = True

    
    def handleReq(self, session):
        if self.params["playlistId"] and self.params["name"]:
            raise MissingParam(
                "Can't supply playlistId and name at the same time")
        elif (not self.params["playlistId"] and not self.params["name"]):
            raise MissingParam("Must supply playlistId or name")

        if self.params["playlistId"]:
            # Update/append case
            plist = session.query(PlayList).filter(
                PlayList.id == self.params["playlistId"]).one_or_none()
            if plist is None:
                raise MissingParam("Invalid playlistId: pl-%s" % sid)
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
            pltrack = PlayListTrack(track_id=track.id,
                                    playlist_id = plist.id)
            session.add(pltrack)
            self.params["id"] = plist.id

        session.commit()

        # Fun little hack to return the newly created playlist
        return GetPlayList.handleReq(self, session)


addCmd(CreatePlayList)
