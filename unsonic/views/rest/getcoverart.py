import os.path

from pyramid.response import FileResponse

from . import Command, addCmd
from ... import mash


class GetCoverArt(Command):
    name = "getCoverArt.view"
    param_defs = {"id": {"required": True}}

    # FIXME: Do this right once there is art info in mishmash
    def handleReq(self):
        return FileResponse(os.path.join(mash.getPaths(self.settings).values()[0],
                                         "albumart.png"))


addCmd(GetCoverArt)
