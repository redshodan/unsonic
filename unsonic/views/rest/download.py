import xml.etree.ElementTree as ET

from . import (Command, MissingParam, NotFound, addCmd, fillAlbum, fillArtist,
               fillSong)
from .stream import Stream
from . import Command, addCmd, bool_t, track_t


class Download(Stream):
    name = "download.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        }

    def __init__(self, req):
        super().__init__(req)

addCmd(Download)
