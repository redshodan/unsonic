from . import Command, addCmd


class Ping(Command):
    name = "ping.view"
    param_defs = {}

    def handleReq(self):
        return self.makeResp({"name":"unsonic"})


addCmd(Ping)
