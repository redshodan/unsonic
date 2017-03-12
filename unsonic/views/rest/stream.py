from pyramid.response import FileResponse

from . import Command, registerCmd, bool_t, track_t, int_t
from ...models import Track


@registerCmd
class Stream(Command):
    name = "stream.view"
    param_defs = {
        "id": {"required": True, "type": track_t},
        "maxBitRate": {"type": int_t},
        "format": {"values": ["mp3", "flv", "raw"]},
        "timeOffset": {"type": int_t},
        "size": {"type": int_t},
        "estimateContentLength": {"default": False, "type": bool_t},
        }
    dbsess = True


    def handleReq(self, session):
        row = session.query(Track).filter(Track.id == self.params["id"]).all()[0]
        return FileResponse(row.path)
