import xml.etree.ElementTree as ET
import datetime

from . import Command, registerCmd, fillTrack
from ...models import dbinfo, Track


@registerCmd
class GetNowPlaying(Command):
    name = "getNowPlaying.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        np = ET.Element("nowPlaying")
        for name, user in dbinfo.users.items():
            row = session.query(Track).filter(
                Track.id == user.listening).one_or_none()
            if not row:
                continue
            minutes_ago = user.listening_since - datetime.datetime.now()
            minutes_ago = int(round(minutes_ago.total_seconds() / 60))
            track = fillTrack(session, row, name="entry")
            track.set("playerId", "0")
            track.set("minutesAgo", str(minutes_ago))
            track.set("username", name)
            np.append(track)

        return self.makeResp(child=np)
