import xml.etree.ElementTree as ET

from . import Command, registerCmd, NoPerm, fillUser
from ...models import getUsers


@registerCmd
class GetUsers(Command):
    name = "getUsers.view"
    param_defs = {}
    dbsess = True


    def handleReq(self, session):
        if not self.req.authed_user.isAdmin():
            raise NoPerm("Can not get user list unless you are an admin")

        users = ET.Element("users")
        for user in getUsers(session):
            users.append(fillUser(session, user))

        return self.makeResp(child=users)
