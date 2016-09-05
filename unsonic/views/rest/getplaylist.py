import xml.etree.ElementTree as ET

from . import Command, addCmd, fillPlayList, fillSong, playlist_t, MissingParam
from ...models import (getUserByName, Session, PlayList, PlayListTrack,
                       PlayListUser)


class GetPlayList(Command):
    name = "getPlaylist.view"
    param_defs = {"id": {"required": True, "type": playlist_t}}
    dbsess = True

    
    def handleReq(self, session):
        playlists = ET.Element("playlist")
        plrow = session.query(PlayList).filter(PlayList.id ==
                                                 self.params["id"]).all()
        if not len(plrow):
            raise MissingParam("Invalid playlist id: %s" % self.params["id"])
        plrow = plrow[0]
        
        playlist = fillPlayList(plrow)
        for pltrack in plrow.tracks:
            entry = fillSong(pltrack.track, name="entry")
            playlist.append(entry)

        return self.makeResp(child=playlist)


addCmd(GetPlayList)
