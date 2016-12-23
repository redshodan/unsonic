from . import addCmd
from .getstarred import GetStarred


class GetStarred2(GetStarred):
    name = "getStarred2.view"
    param_defs = GetStarred.param_defs
    dbsess = True


    def __init__(self, req):
        super().__init__(req)
        self.starred = "starred2"


addCmd(GetStarred2)
