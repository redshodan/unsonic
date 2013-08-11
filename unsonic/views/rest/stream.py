from pyramid.response import FileResponse

from . import Command, addCmd, bool_t, track_t
from ...models import DBSession, Track


class Stream(Command):
    name = "stream.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        "maxBitRate": {"type": int},
        "format": {"values": ["mp3", "flv", "raw"]},
        "timeOffset": {"type": int},
        "size": {"type": int},
        "estimateContentLength": {"default": False, "type": bool_t},
        }

    def handleReq(self):
        row = DBSession.query(Track).filter(Track.id == self.params["id"]).all()[0]
        return FileResponse(row.path)


addCmd(Stream)
