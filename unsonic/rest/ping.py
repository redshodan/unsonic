from . import Command, addCmd


class Ping(Command):
    def __init__(self):
        super(Ping, self).__init__("ping")

    def handleReq(self, req):
        return self.makeResp({"name":"unsonic"})


addCmd(Ping())
