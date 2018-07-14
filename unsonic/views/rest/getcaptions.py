from . import Command, registerCmd, NotFound


# Stubbed out, not implementing
@registerCmd
class GetCaptions(Command):
    name = "getCaptions.view"
    param_defs = {
        "id": {"type": str, "required": True},
        "format": {"type": str},
    }
    dbsess = True


    def handleReq(self, session):
        raise NotFound()
