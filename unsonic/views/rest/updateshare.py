from . import Command, registerCmd, share_t, str_t, datetime_t, MissingParam
from ...models import Share


@registerCmd
class UpdateShare(Command):
    name = "updateShare.view"
    param_defs = {
        "id": {"type": share_t, "required": True},
        "description": {"type": str_t},
        "expires": {"type": datetime_t},
        }
    dbsess = True


    def handleReq(self, session):
        id = self.params["id"]
        share = session.query(Share).filter(Share.id == id).one_or_none()
        if not share:
            raise MissingParam(f"Invalid share id: {id}")

        if self.params["description"]:
            share.description = self.params["description"]
        if self.params["expires"]:
            share.expires = self.params["expires"]

        return self.makeResp()
