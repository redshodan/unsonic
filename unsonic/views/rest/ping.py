from . import Command, registerCmd


@registerCmd
class Ping(Command):
    name = "ping.view"
    param_defs = {}

    def handleReq(self):
        return self.makeResp()
