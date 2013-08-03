from . import Command, addCmd, bool_t, track_t

from pyramid.response import FileResponse

from mishmash.orm import Track, Artist, Album, Meta, Label


class Stream(Command):
    def __init__(self):
        super(Stream, self).__init__("stream")
        self.param_defs = {
            "id": {"required": True, "type": track_t},
            "maxBitRate": {"type": int},
            "format": {"values": ["mp3", "flv", "raw"]},
            "timeOffset": {"type": int},
            "size": {"type": int},
            "estimateContentLength": {"default": False, "type": bool_t},
            }

    def handleReq(self, req):
        session = self.mash_db.Session()
        row = session.query(Track).filter(Track.id == self.params["id"]).all()[0]
        return FileResponse(row.path)


addCmd(Stream())
