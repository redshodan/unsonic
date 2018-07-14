from . import Command, registerCmd, track_t, NotFound


# Stubbed out, not implementing
@registerCmd
class HLS(Command):
    name = "hls.m3u8"
    param_defs = {
        "id": {"type": track_t, "required": True},
        "bitRate": {"type": str},
        "audioTrack": {"type": str}
    }
    dbsess = True


    def handleReq(self, session):
        raise NotFound()
