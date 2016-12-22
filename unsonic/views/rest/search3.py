import time
import xml.etree.ElementTree as ET

from . search2 import Search2
from . import (Command, addCmd, bool_t, positive_t, fillArtist, fillAlbum,
               fillTrack)
from ...models import Session, Artist, Album, Track


class Search3(Search2):
    name = "search3.view"
    param_defs = Search2.param_defs
    dbsess = True


addCmd(Search3)
