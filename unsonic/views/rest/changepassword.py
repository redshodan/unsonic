from . import Command, registerCmd, InternalError, NoPerm
from ...models import User


@registerCmd
class ChangePassword(Command):
    name = "changePassword.view"
    param_defs = {
        "username": {},
        "password": {"required": True},
        }
    dbsess = True


    def handleReq(self, session):
        name = self.params["username"]
        if not name:
            name = self.req.authed_user.name
        if ((name != self.req.authed_user.name) and
                not self.req.authed_user.isAdmin()):
            raise NoPerm("Can not change a user's password unless you "
                         "are an admin")

        user = session.query(User).filter(User.name == name).one_or_none()
        if not user:
            raise InternalError("User '%s' does not exist" % name)

        user.password = self.params["password"]
        session.add(user)

        return self.makeResp()
