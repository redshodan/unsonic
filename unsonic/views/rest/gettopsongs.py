import xml.etree.ElementTree as ET

from . import Command, NotFound, registerCmd, int_t, str_t, fillTrackUser
from ...models import Artist, Album, Track
from ...log import log


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

        try:
            lf_client = self.req.authed_user.lastfm
            lf_artist = lf_client.get_artist(self.params["artist"])
            if not lf_artist:
                raise NotFound("Artist not found")
            lf_tops = lf_artist.get_top_tracks(limit=self.params["count"])

            if lf_tops:
                for top in lf_tops:
                    artist = session.query(Artist).filter(
                        Artist.name ==
                        top.item.get_artist().get_name()).one_or_none()
                    if artist:
                        track = None
                        if (top.item.get_album() and
                                top.item.get_album().get_title()):
                            album = session.query(Album).\
                                    filter(
                                        Album.artist_id == artist.id,
                                        Album.title ==
                                        top.item.get_album().get_title()).\
                                    one_or_none()
                            if album:
                                track = session.query(Track).\
                                        filter(
                                            Track.artist_id == artist.id,
                                            Track.album_id == album.id,
                                            Track.title ==
                                            top.item.get_title()).one_or_none()
                        if not track:
                            track = session.query(Track).filter(
                                Track.artist_id == artist.id,
                                Track.title == top.item.get_title()).all()
                            if track and len(track) > 0:
                                track = track[0]
                            else:
                                track = None
                        if track:
                            songs.append(fillTrackUser(session, track, None,
                                                       self.req.authed_user))
        except Exception as e:
            log.error("Error talking to LastFM: " + str(e))
            return self.makeResp(status=504)

        return self.makeResp(child=songs)
