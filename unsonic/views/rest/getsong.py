from . import registerCmd
from .getmusicdirectory import GetMusicDirectory


@registerCmd
class GetSong(GetMusicDirectory):
    name = "getSong.view"

    def __init__(self, req):
        super(GetSong, self).__init__(req)
        self.setParams(dir_param="song", album_param="song", track_param="song")
