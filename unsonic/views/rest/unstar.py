from . import Command, registerCmd, playable_id_t, MissingParam
from ...models import rateItem


@registerCmd
class UnStar(Command):
    name = "unstar.view"
    param_defs = {
        "id": {"type": playable_id_t},
        "ablumId": {"type": playable_id_t},
        "artistId": {"type": playable_id_t},
        }

    def handleReq(self):
        if self.params["id"]:
            id = self.params["id"]
        elif self.params["albumId"]:
            id = self.params["albumId"]
        elif self.params["artistId"]:
            id = self.params["artistId"]
        else:
            raise MissingParam("Missing a valid id parameter")

        rateItem(self.req.authed_user.id, id, starred=True)
        return self.makeResp()
