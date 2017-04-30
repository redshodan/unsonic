from . import Command, registerCmd, NotFound
from ...models import Image, getUserByName


@registerCmd
class GetAvatar(Command):
    name = "getAvatar.view"
    param_defs = {
        "username": {"required": True},
        }
    dbsess = True


    def handleReq(self, session):
        if self.req.authed_user.name == self.params["username"]:
            db_user = self.req.authed_user
        else:
            db_user = getUserByName(session, self.params["username"])
        if not db_user:
            raise NotFound("User not found")
        row = session.query(Image).\
                  filter(Image.id == db_user.avatar).one_or_none()
        if not row:
            raise NotFound("User has no avatar")
        return self.makeBinaryResp(row.data, row.mime_type, row.md5)
