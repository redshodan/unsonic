import xml.etree.ElementTree as ET
import pylast

from . import Command, NotFound, registerCmd, int_t, track_t, fillTrackUser
from ... import lastfm
from ...models import Track, getPlayable


@registerCmd
class GetSimilarSongs(Command):
    name = "getSimilarSongs.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        "count": {"default": 50, "type": int_t},
    }
    dbsess = True

    def handleReq(self, session):
        row = session.query(Track).filter(Track.id == self.params["id"]).one()
        if row is None:
            raise NotFound("Item not found")

        lf_client = self.req.authed_user.lastfm
        lf_track = lf_client.get_track(row.artist.name, row.title)
        if not lf_track:
            raise NotFound("Item not found in LastFM")
        # FIXME: Once pylast updates, remove this check. Bound to 2.1.0 by reqs.
        if pylast.__version__ != "2.1.0":
            lf_ssongs = lf_track.get_similar(limit=self.params["count"])
        else:
            lf_ssongs = lf_track.get_similar()

        ssong = ET.Element("similarSongs")

        for lf_song in lf_ssongs:
            lf_track = session.query(Track).filter(
                Track.title == lf_song.item.get_title()).one_or_none()
            if lf_track:
                ssong.append(fillTrackUser(session, lf_track, None,
                                           self.req.authed_user, "song"))

        return self.makeResp(child=ssong)
