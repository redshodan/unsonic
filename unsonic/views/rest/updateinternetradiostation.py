from . import Command, registerCmd, iradio_t, NotFound
from ...models import InternetRadio


@registerCmd
class UpdateRadioInternetStation(Command):
    name = "updateInternetRadioStation.view"
    param_defs = {
        "id": {"type": iradio_t, "required": True},
        "name": {"type": str, "required": True},
        "streamUrl": {"type": str, "required": True},
        "homepageUrl": {"type": str},
        }
    dbsess = True


    def handleReq(self, session):
        ir = session.query(InternetRadio).filter(
            InternetRadio.id == self.params["id"],
            InternetRadio.user_id == self.req.authed_user.id).one_or_none()
        if not ir:
            raise NotFound()

        ir.name = self.params["name"]
        ir.stream_url = self.params["streamUrl"]
        ir.homepage_url = self.params["homepageUrl"]
        session.add(ir)

        return self.makeResp()
