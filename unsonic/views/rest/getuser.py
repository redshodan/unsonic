import transaction, datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import Command, addCmd, InternalError, MissingParam, NoPerm, fillUser
from ...models import getUserByName
from ...auth import Roles


class GetUser(Command):
    name = "getUser.view"
    param_defs = {
        "username": {"required": True},
        }
    dbsess = True

    
    def handleReq(self, session):
        if self.req.authed_user.name == self.params["username"]:
            db_user = self.req.authed_user
        elif self.req.authed_user.isAdmin():
            db_user = getUserByName(session, self.params["username"])
        else:
            raise NoPerm("Can not view a user other than yourself unless you "
                         "are an admin")

        return self.makeResp(child=fillUser(session, db_user))


addCmd(GetUser)
