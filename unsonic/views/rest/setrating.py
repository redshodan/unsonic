from . import Command, registerCmd, playable_id_t, int_t
from ...models import rateItem


@registerCmd
class SetRating(Command):
    name = "setRating.view"
    param_defs = {
        "id": {"type": playable_id_t, "required": True},
        "rating": {"type": int_t, "required": True},
        }
    dbsess = True


    def handleReq(self, session):
        rateItem(session, self.req.authed_user.id, self.params["id"],
                 rating=self.params["rating"])
        return self.makeResp()
