from . import Command, addCmd

from pyramid.response import FileResponse

from mishmash.orm import Track, Artist, Album, Meta, Label


class Stream(Command):
    def __init__(self):
        super(Stream, self).__init__("stream")
        
    def handleReq(self, req):
        # Param handling
        mbr, form, offset, size, ecl, track_id = \
          self.getParams(req, (("maxBitRate", None), ("format", None),
                                        ("timeOffset", None), ("size", None),
                                        ("estimateContentLength", None)),
                                  (("id", None),))
        if not track_id.startswith("tr-"):
            raise Exception("Not a track")
        track_id = int(track_id[3:])

        # Processing
        session = self.mash_db.Session()
        row = session.query(Track).filter(Track.id == track_id).all()[0]
        return FileResponse(row.path)


addCmd(Stream())
