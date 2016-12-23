from . getalbumlist import GetAlbumList
from . import addCmd


class GetAlbumList2(GetAlbumList):
    name = "getAlbumList2.view"
    param_defs = GetAlbumList.param_defs
    dbsess = True


addCmd(GetAlbumList2)
