import transaction
import xml.etree.ElementTree as ET

from . import Command, addCmd, InternalError, MissingParam
from ...models import getUserByName, DBSession, PlayList, PlayListTrack, Track


class CreatePlayList(Command):
    name = "createPlaylist.view"
    param_defs = {
        "playlistId": {},
        "name": {},
        "songId": {},
        }
    
    def handleReq(self):
        if "playlistId" in self.params and "name" in self.params:
            raise MissingParam(
                "Can't supply playlistId and name at the same time")
        elif ("playlistId" not in self.params and
              "name" not in self.params):
            raise MissingParam("Must supply playlistId or name")
        
        if "playlistId" in self.params:
            print "Update!"
        else:
            with transaction.manager:
                plist = PlayList(owner_id=self.req.authed_user.id,
                                 name=self.params["name"])
                DBSession.add(plist)
                for sid in self.params.getall("songId"):
                    if not sid.startswith("tr-"):
                        DBSession.rollback()
                        raise MissingParam("Invalid songId: %s" % sid)
                    sid = int(sid[3:])
                    track = DBSession.query(Track).filter(Track.id == sid).one()
                    if track is None:
                        DBSession.rollback()
                        raise MissingParam("Invalid songId: %s" % sid)
                    pltrack = PlayListTrack(track_id=track.id,
                                            playlist_id = plist.id)
                    DBSession.add(pltrack)

        return self.makeResp()


addCmd(CreatePlayList)
