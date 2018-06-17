from . import registerCmd
from .createuser import CreateUser


@registerCmd
class UpdateUser(CreateUser):
    name = "updateUser.view"
    param_defs = CreateUser.param_defs
    dbsess = True


    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        super().setUpdate(True)
