import xml.etree.ElementTree as ET

from . import Command, NotFound, registerCmd, int_t, str_t, fillTrackUser
from ...models import Artist, Track


@registerCmd
class GetTopSongs(Command):
    name = "getTopSongs.view"
    param_defs = {
        "artist": {"required": True, "type": str_t},
        "count": {"default": 50, "type": int_t},
    }
    dbsess = True

    def handleReq(self, session):
        songs = ET.Element("topSongs")

        lf_client = self.req.authed_user.lastfm
        lf_artist = lf_client.get_artist(self.params["artist"])
        if not lf_artist:
            raise NotFound("Artist not found")
        lf_tops = lf_artist.get_top_tracks(limit=self.params["count"])
        print(lf_tops)
        if lf_tops:
            for top in lf_tops:
                artist = session.query(Artist).filter(
                    Artist.name ==
                    top.item.get_artist().get_name()).one_or_none()
                if artist:
                    track = session.query(Track).filter(
                        Track.artist_id == artist.id,
                        Track.title == top.item.get_title()).one_or_none()
                    if track:
                        songs.append(fillTrackUser(session, track, None,
                                                   self.req.authed_user))

        return self.makeResp(child=songs)
