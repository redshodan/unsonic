from . import Command, addCmd


class Ping(Command):
    def __init__(self):
        super(Ping, self).__init__("ping")

    def handleReq(self, req):
        # Processing
        return self.makeResp(req, {"name":"unsonic"})


addCmd(Ping())
