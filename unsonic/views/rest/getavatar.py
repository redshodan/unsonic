from . import Command, addCmd
from ...models import Image, getUserByName


class GetAvatar(Command):
    name = "getAvatar.view"
    param_defs = {
        "username": {"required": True},
        }
    dbsess = True


    def handleReq(self, session):
        if self.req.authed_user.name == self.params["username"]:
            db_user = self.req.authed_user
        elif self.req.authed_user.isAdmin():
            db_user = getUserByName(session, self.params["username"])
        row = session.query(Image).filter(Image.id == db_user.avatar).one()

        return self.makeBinaryResp(row.data, row.mime_type, row.md5)


addCmd(GetAvatar)
