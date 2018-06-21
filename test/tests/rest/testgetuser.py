from unsonic.views.rest.getuser import GetUser
from . import buildCmd, checkResp


def testGetUser(session):
    cmd = buildCmd(session, GetUser, {"username": "test"})
    resp = checkResp(cmd.req, cmd())
    user = resp.find("{http://subsonic.org/restapi}user")
    assert user.get("username") == "test"
