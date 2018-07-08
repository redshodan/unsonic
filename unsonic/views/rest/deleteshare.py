from . import Command, registerCmd, share_t, MissingParam
from ...models import Share


@registerCmd
class DeleteShare(Command):
    name = "deleteShare.view"
    param_defs = {"id": {"required": True, "type": share_t}}
    dbsess = True


    def handleReq(self, session):
        res = session.query(Share). \
                    filter(Share.id == self.params["id"]). \
                    filter(Share.user_id == self.req.authed_user.id)
        if not res.one_or_none():
            raise MissingParam("Invalid share id: %s" % self.params["id"])
        res.delete()

        return self.makeResp()
