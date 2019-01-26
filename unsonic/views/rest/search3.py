from . search2 import Search2
from . import registerCmd, fillAlbumID3


@registerCmd
class Search3(Search2):
    name = "search3.view"
    param_defs = Search2.param_defs
    dbsess = True


    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        self.setParams("searchResult3", self.fillAlbum3)


    def fillAlbum3(self, session, row):
        return fillAlbumID3(session, row, self.req.authed_user, False)
