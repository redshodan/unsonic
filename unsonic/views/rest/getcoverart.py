import os.path
from . import Command, addCmd

from pyramid.response import FileResponse

from ... import db


class GetCoverArt(Command):
    def __init__(self):
        super(GetCoverArt, self).__init__("getCoverArt")

    # FIXME: Do this right once there is art info in mishmash
    def handleReq(self, req):
        cover_id = self.getParams(req, required=(("id", None),))
        return FileResponse(os.path.join(db.getMashPaths(self.mash_settings).values()[0],
                                         "albumart.png"))


addCmd(GetCoverArt())
