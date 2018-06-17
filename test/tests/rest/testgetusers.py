from unsonic.views.rest.getusers import GetUsers
from . import buildCmd, checkResp


def testGetUsers(session):
    cmd = buildCmd(session, GetUsers, {}, "admin")
    resp = checkResp(cmd.req, cmd())
    users = resp.find("{http://subsonic.org/restapi}users")
    for user in users.iter("{http://subsonic.org/restapi}user"):
        assert user.get("username") in ["test", "admin"]
