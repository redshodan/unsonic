from . import Command, registerCmd


@registerCmd
class AddChatMessage(Command):
    name = "addChatMessage.view"
    param_defs = {"message": {}}
    dbsess = True


    def handleReq(self, session):
        return self.makeResp()
