from .getalbuminfo import GetAlbumInfo
from . import registerCmd


# TODO: Actually implement
@registerCmd
class GetAlbumInfo2(GetAlbumInfo):
    name = "getAlbumInfo2.view"
    param_defs = GetAlbumInfo.param_defs
    dbsess = True
