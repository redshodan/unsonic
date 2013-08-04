import os.path
from . import Command, addCmd

from pyramid.response import FileResponse

from ... import db


class GetCoverArt(Command):
    name = "getCoverArt.view"
    param_defs = {"id": {"required": True}}

    # FIXME: Do this right once there is art info in mishmash
    def handleReq(self):
        return FileResponse(os.path.join(db.getMashPaths(self.mash_settings).values()[0],
                                         "albumart.png"))


addCmd(GetCoverArt)
