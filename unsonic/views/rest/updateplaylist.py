from . import (Command, registerCmd, MissingParam, track_t, bool_t, positive_t,
               playlist_t)
from ...models import PlayList, PlayListTrack, Track


@registerCmd
class UpdatePlayList(Command):
    name = "updatePlaylist.view"
    param_defs = {
        "playlistId": {"required": True, "type": playlist_t},
        "name": {},
        "comment": {},
        "public": {"type": bool_t},
        "songIdToAdd": {"multi": True, "type": track_t},
        "songIndexToRemove": {"multi": True, "type": positive_t},
        }
    dbsess = True


    def handleReq(self, session):
        plist = session.query(PlayList).filter(
            PlayList.id == self.params["playlistId"]).one_or_none()
        if plist is None:
            raise MissingParam("Invalid playlistId: pl-%s" %
                               self.params["playlistId"])

        if self.params["name"]:
            plist.name = self.params["name"]
        if self.params["comment"]:
            plist.comment = self.params["comment"]
        if self.params["public"] is not None:
            plist.public = self.params["public"]

        # Delete songs
        if len(self.params["songIndexToRemove"]):
            tracks = session.query(PlayListTrack).filter(
                PlayListTrack.playlist_id == self.params["playlistId"]).all()
            tracks_len = len(tracks)
            for index in self.params["songIndexToRemove"]:
                if index >= tracks_len:
                    raise MissingParam("Invalid songIndexToRemove: %d" % index)
                res = session.query(PlayListTrack). \
                          filter(PlayListTrack.id == tracks[index].id)
                if not res.one_or_none():
                    raise MissingParam("Invalid track id: tr-%s" %
                                       tracks[index].id)
                res.delete()

        # Add songs
        for sid in self.params["songIdToAdd"]:
            track = session.query(Track).filter(Track.id == sid).one()
            if track is None:
                raise MissingParam("Invalid songId: tr-%s" % sid)
            pltrack = PlayListTrack(track_id=track.id, playlist_id=plist.id)
            session.add(pltrack)

        plist.changed = plist.changed.now()

        return self.makeResp()
