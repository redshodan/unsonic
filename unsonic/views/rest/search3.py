from . search2 import Search2
from . import registerCmd


@registerCmd
class Search3(Search2):
    name = "search3.view"
    param_defs = Search2.param_defs
    dbsess = True
