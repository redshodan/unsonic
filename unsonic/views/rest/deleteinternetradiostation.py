from . import Command, registerCmd, iradio_t
from ...models import InternetRadio


@registerCmd
class DeleteRadioInternetStation(Command):
    name = "deleteInternetRadioStation.view"
    param_defs = {"id": {"type": iradio_t, "required": True}}
    dbsess = True


    def handleReq(self, session):
        session.query(InternetRadio).filter(
            InternetRadio.id == self.params["id"],
            InternetRadio.user_id == self.req.authed_user.id).delete()

        return self.makeResp()
