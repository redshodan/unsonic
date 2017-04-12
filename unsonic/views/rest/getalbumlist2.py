from . getalbumlist import GetAlbumList
from . import registerCmd, fillAlbumID3


@registerCmd
class GetAlbumList2(GetAlbumList):
    name = "getAlbumList2.view"
    param_defs = GetAlbumList.param_defs
    dbsess = True


    def __init__(self, route, req):
        super().__init__(route, req)
        self.setParams("albumList2")


    def processRows(self, session, alist, result):
        for row in result:
            album = fillAlbumID3(session, row, self.req.authed_user, False)
            alist.append(album)
