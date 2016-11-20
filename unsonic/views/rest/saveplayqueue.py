import xml.etree.ElementTree as ET

from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from . import (Command, addCmd, InternalError, MissingParam, NoPerm, fillUser,
               bool_t, bitrate_t, playable_id_t)
from ...models import User, Role
from ...auth import Roles


class SavePlayQueue(Command):
    name = "savePlayQueue.view"
    param_defs = {
        "id": {"required": True, "type": playable_id_t, "multi": True},
        "current": {},
        "position": {},
        }
    dbsess = True


    def handleReq(self, session):
        print(self.params)

        # name = self.params["username"]
        # user = session.query(User).filter(User.name == name).one_or_none()
        # if user and not self.update:
        #     raise InternalError("User '%s' already exists" % name)
        # if not user and self.update:
        #     raise InternalError("User '%s' does not exist" % name)

        # if not self.update:
        #     user = User()
        # user.name=name
        # user.password=self.params["password"]
        # user.email=self.params["email"]
        # user.maxbitrate=self.params["maxBitRate"]
        # session.add(user)
        # session.flush()

        # for role, un_role in self.role_names.items():
        #     if (self.params[role] and
        #         (session.query(Role).filter(Role.user_id == user.id).\
        #          filter(Role.name == un_role).one_or_none()) is None):
        #         session.add(Role(user_id=user.id, name=un_role))
        #     if self.params[role] is False:
        #         session.query(Role).filter(Role.user_id == user.id).\
        #           filter(Role.name == un_role).delete()

        # if not self.update:
        #     session.add(Role(user_id=user.id, name=Roles.USERS))
        #     session.add(Role(user_id=user.id, name=Roles.REST))

        return self.makeResp()


addCmd(SavePlayQueue)
