import xml.etree.ElementTree as ET

from . import Command, addCmd, InternalError, MissingParam
from ...models import Session, PlayList, PlayListTrack, Track


class CreatePlayList(Command):
    name = "createPlaylist.view"
    param_defs = {
        "playlistId": {},
        "name": {},
        "songId": {},
        }
    dbsess = True

    
    def handleReq(self, session):
        if "playlistId" in self.params and "name" in self.params:
            raise MissingParam(
                "Can't supply playlistId and name at the same time")
        elif ("playlistId" not in self.params and
              "name" not in self.params):
            raise MissingParam("Must supply playlistId or name")
        
        if "playlistId" in self.params:
            print("Update!")
        else:
            plist = PlayList(user_id=self.req.authed_user.id,
                             name=self.params["name"])
            session.add(plist)
            for sid in self.params.getall("songId"):
                if not sid.startswith("tr-"):
                    session.rollback()
                    raise MissingParam("Invalid songId: %s" % sid)
                sid = int(sid[3:])
                track = session.query(Track).filter(Track.id == sid).one()
                if track is None:
                    session.rollback()
                    raise MissingParam("Invalid songId: %s" % sid)
                pltrack = PlayListTrack(track_id=track.id,
                                        playlist_id = plist.id)
                session.add(pltrack)

        return self.makeResp()


addCmd(CreatePlayList)
