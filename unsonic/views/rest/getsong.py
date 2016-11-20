import xml.etree.ElementTree as ET

from . import (Command, MissingParam, NotFound, addCmd, fillAlbum, fillArtist,
               fillTrack)
from .getmusicdirectory import GetMusicDirectory
from ...models import Session, Artist, Album, Track
from ... import mash


class GetSong(GetMusicDirectory):
    name = "getSong.view"

    def __init__(self, req):
        super(GetSong, self).__init__(req)
        self.setParams(dir_param="song", album_param="song", track_param="song")

addCmd(GetSong)
