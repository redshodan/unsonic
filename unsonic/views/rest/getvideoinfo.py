from . import Command, registerCmd, NotFound


# Stubbed out, not implementing
@registerCmd
class GetVideoInfo(Command):
    name = "getVideoInfo.view"
    param_defs = {"id": {"type": str, "required": True}}
    dbsess = True


    def handleReq(self, session):
        raise NotFound()
