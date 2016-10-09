import transaction, datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import Command, addCmd, InternalError, MissingParam, NoPerm
from ...models import getUserByName
from ...auth import Roles


class GetUser(Command):
    name = "getUser.view"
    param_defs = {
        "username": {"required": True},
        }
    dbsess = True

    
    def handleReq(self, session):
        user = ET.Element("user")
        if self.req.authed_user.name == self.params["username"]:
            db_user = self.req.authed_user
        elif self.req.authed_user.isAdmin():
            db_user = getUserByName(session, self.params["username"])
        else:
            raise NoPerm("Can not view a user other than yourself unless you "
                         "are an admin")

        user.set("username", db_user.name)
        user.set("email", db_user.email if db_user.email else "")
        user.set("scrobblingEnabled", "true" if db_user.scrobbling else "false")
        for role in Roles.subsonic_roles:
            user.set("%sRole" % role,
                     "true" if role in db_user.roles else "false")
        
        return self.makeResp(child=user)


addCmd(GetUser)
