from . import Command, addCmd


class AddChatMessage(Command):
    name = "addChatMessage.view"
    param_defs = {"message": {}}
    dbsess = True


    def handleReq(self, session):
        return self.makeResp()


addCmd(AddChatMessage)
