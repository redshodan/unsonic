import transaction, datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import (Command, addCmd, InternalError, MissingParam, NoPerm, fillUser,
               bool_t, bitrate_t)
from ...models import User, Role
from ...auth import Roles


class DeleteUser(Command):
    name = "deleteUser.view"
    param_defs = {
        "username": {"required": True},
        }
    dbsess = True


    def handleReq(self, session):
        name = self.params["username"]
        if ((name != self.req.authed_user.name) and
            not self.req.authed_user.isAdmin()):
            raise NoPerm("Can not delete a user unless you are an admin")

        session.query(User).filter(User.name == name).delete()
        
        return self.makeResp()


addCmd(DeleteUser)
