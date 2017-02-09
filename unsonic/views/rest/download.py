from . import addCmd, track_t
from .stream import Stream


class Download(Stream):
    name = "download.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        }

    def __init__(self, req):
        super().__init__(req)


addCmd(Download)
