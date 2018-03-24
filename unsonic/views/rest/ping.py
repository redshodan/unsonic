from . import Command, registerCmd


@registerCmd
class Ping(Command):
    name = "ping.view"
    param_defs = {}

    def handleReq(self, session=None):
        return self.makeResp()
