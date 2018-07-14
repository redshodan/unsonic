import xml.etree.ElementTree as ET

from . import Command, NotFound, registerCmd, int_t, track_t, fillTrackUser
from ...models import Track


@registerCmd
class GetSimilarSongs(Command):
    name = "getSimilarSongs.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        "count": {"default": 50, "type": int_t},
    }
    dbsess = True

    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        self.setParams()

    def setParams(self, tag_name="similarSongs"):
        self.tag_name = tag_name

    def handleReq(self, session):
        row = session.query(Track).filter(Track.id == self.params["id"]).one()
        if row is None:
            raise NotFound("Item not found")

        lf_client = self.req.authed_user.lastfm
        lf_track = lf_client.get_track(row.artist.name, row.title)
        if not lf_track:
            raise NotFound("Item not found in LastFM")
        lf_ssongs = lf_track.get_similar(limit=self.params["count"])

        ssong = ET.Element(self.tag_name)

        for lf_song in lf_ssongs:
            lf_track = session.query(Track).filter(
                Track.title == lf_song.item.get_title()).one_or_none()
            if lf_track:
                ssong.append(fillTrackUser(session, lf_track, None,
                                           self.req.authed_user, "song"))

        return self.makeResp(child=ssong)
