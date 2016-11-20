from . import addCmd
from .createuser import CreateUser


class UpdateUser(CreateUser):
    name = "updateUser.view"
    param_defs = CreateUser.param_defs
    dbsess = True


    def __init__(self, req):
        super().__init__(req)
        super().setUpdate(True)


addCmd(UpdateUser)
