from .getsimilarsongs import GetSimilarSongs
from . import registerCmd


# TODO: Actually implement
@registerCmd
class GetSimilarSongs2(GetSimilarSongs):
    name = "getSimilarSongs2.view"
    param_defs = GetSimilarSongs.param_defs
    dbsess = True
