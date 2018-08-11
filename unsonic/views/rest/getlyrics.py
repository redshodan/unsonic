import xml.etree.ElementTree as ET
import lyricwikia

from . import Command, NotFound, registerCmd, track_t
from ...models import Track
from ...log import log


@registerCmd
class GetLyrics(Command):
    name = "getLyrics.view"
    param_defs = {
        "id": {"type": track_t},
        "artist": {"type": str},
        "title": {"type": str},
    }
    dbsess = True

    def handleReq(self, session):
        id = self.params["id"]
        artist = self.params["artist"]
        title = self.params["title"]

        if id:
            track = session.query(Track).filter(Track.id == id).one_or_none()
            if not track:
                raise NotFound("Item not found")
            artist = track.artist.name
            title = track.title
        elif not artist and not title:
            raise NotFound("Item not found")

        try:
            resp = lyricwikia.get_lyrics(artist, title)
        except lyricwikia.LyricsNotFound:
            raise NotFound("Item not found")
        except Exception as e:
            log.error("Error talking to LyricWikia: " + str(e))
            return self.makeResp(status=504)

        lyrics = ET.Element("lyrics")
        lyrics.set("artist", artist)
        lyrics.set("title", title)
        lyrics.text = resp

        return self.makeResp(child=lyrics)
