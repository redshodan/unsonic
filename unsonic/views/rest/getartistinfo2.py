from .getartistinfo import GetArtistInfo
from . import registerCmd


# TODO: Actually implement
@registerCmd
class GetArtistInfo2(GetArtistInfo):
    name = "getArtistInfo2.view"
    param_defs = GetArtistInfo.param_defs
    dbsess = True
