from .getsimilarsongs import GetSimilarSongs
from . import registerCmd


# TODO: Actually implement
@registerCmd
class GetSimilarSongs2(GetSimilarSongs):
    name = "getSimilarSongs2.view"
    param_defs = GetSimilarSongs.param_defs
    dbsess = True

    def __init__(self, route, req, session=None):
        super().__init__(route, req, session=session)
        self.setParams("similarSongs2")
