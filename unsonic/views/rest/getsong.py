from . import registerCmd
from .getmusicdirectory import GetMusicDirectory


@registerCmd
class GetSong(GetMusicDirectory):
    name = "getSong.view"

    def __init__(self, route, req, session=None):
        super(GetSong, self).__init__(route, req, session)
        self.setParams(dir_param="song", album_param="song", track_param="song")
