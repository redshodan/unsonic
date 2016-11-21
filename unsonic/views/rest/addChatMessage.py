import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import (Command, addCmd, InternalError, MissingParam, NoPerm)


class AddChatMessage(Command):
    name = "addChatMessage.view"
    param_defs = {"since": {}}
    dbsess = True


    def handleReq(self, session):
        return self.makeResp()


addCmd(AddChatMessage)
