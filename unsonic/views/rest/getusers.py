import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import Command, addCmd, InternalError, MissingParam, NoPerm, fillUser
from ...models import User
from ... import auth


class GetUsers(Command):
    name = "getUsers.view"
    param_defs = {}
    dbsess = True

    
    def handleReq(self, session):
        if not self.req.authed_user.isAdmin():
            raise NoPerm("Can not get user list unless you are an admin")

        users = ET.Element("users")
        for db_user in session.query(User):
            users.append(fillUser(session, auth.User(db_user)))
        
        return self.makeResp(child=users)


addCmd(GetUsers)
