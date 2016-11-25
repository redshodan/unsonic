import xml.etree.ElementTree as ET

from . import Command, addCmd, InternalError, MissingParam, track_t
from ...models import Session, PlayList, PlayListTrack, Track


class CreatePlayList(Command):
    name = "createPlaylist.view"
    param_defs = {
        "playlistId": {},
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
            print("Update!")
        else:
            plist = PlayList(user_id=self.req.authed_user.id,
                             name=self.params["name"])
            session.add(plist)
            for sid in self.params["songId"]:
                track = session.query(Track).filter(Track.id == sid).one()
                if track is None:
                    raise MissingParam("Invalid songId: tr-%s" % sid)
                pltrack = PlayListTrack(track_id=track.id,
                                        playlist_id = plist.id)
                session.add(pltrack)

        return self.makeResp()


addCmd(CreatePlayList)
