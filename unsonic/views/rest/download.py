from . import registerCmd, track_t
from .stream import Stream


@registerCmd
class Download(Stream):
    name = "download.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        }
