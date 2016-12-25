from . getalbumlist import GetAlbumList
from . import (addCmd, fillAlbumID3)


class GetAlbumList2(GetAlbumList):
    name = "getAlbumList2.view"
    param_defs = GetAlbumList.param_defs
    dbsess = True


    def __init__(self, req):
        super().__init__(req)
        self.setParams("albumList2")


    def processRows(self, session, alist, result):
        for row in result:
            album = fillAlbumID3(session, row, self.req.authed_user, False)
            alist.append(album)


addCmd(GetAlbumList2)
