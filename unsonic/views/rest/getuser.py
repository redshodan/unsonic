from . import Command, registerCmd, NoPerm, fillUser, str_t
from ...models import getUserByName


@registerCmd
class GetUser(Command):
    name = "getUser.view"
    param_defs = {
        "username": {"type": str_t},
        }
    dbsess = True


    def handleReq(self, session):
        uname = self.params["username"]
        if not uname:
            user = self.req.authed_user
        elif self.req.authed_user.name == uname:
            user = self.req.authed_user
        elif self.req.authed_user.isAdmin():
            user = getUserByName(session, uname)
        else:
            raise NoPerm("Can not view a user other than yourself unless you "
                         "are an admin")

        return self.makeResp(child=fillUser(session, user))
