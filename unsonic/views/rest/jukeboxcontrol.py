from pyramid.response import FileResponse

from . import Command, registerCmd, int_t, float_t, playable_id_t
from ...models import Track


@registerCmd
class JukeboxControl(Command):
    name = "jukeboxControl.view"
    param_defs = {
        "action": {"required": True,
                   "values": ["get", "status", "set", "start", "stop", "skip",
                              "add", "clear", "remove", "shuffle", "setGain"]},
        "index": {"type": int_t},
        "offset": {"type": int_t},
        "id": {"type": playable_id_t, "multi": True},
        "gain": {"type": float_t},
        }
    dbsess = True


    def handleReq(self, session):
