import xml.etree.ElementTree as ET

from . import (Command, MissingParam, NotFound, addCmd, fillAlbum, fillArtist,
               fillSong)
from .getmusicdirectory import GetMusicDirectory
from ...models import Session, Artist, Album, Track
from ... import mash


class GetAlbum(GetMusicDirectory):
    name = "getAlbum.view"

    def __init__(self, req):
        super(GetAlbum, self).__init__(req)
        self.setParams(dir_param="album", album_param="album",
                       track_param="song")

addCmd(GetAlbum)
