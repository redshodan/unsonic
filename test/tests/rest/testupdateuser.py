from unsonic.models import User
from unsonic.views.rest.getuser import GetUser
from unsonic.views.rest.createuser import CreateUser
from unsonic.views.rest.updateuser import UpdateUser
from . import buildCmd, checkResp


def testUpdateUser(session):
    cmd = buildCmd(session, CreateUser,
                   {"username": "test2", "password": "test2"}, "admin")
    checkResp(cmd.req, cmd())
    row = session.query(User).filter(User.name == "test2").one_or_none()
    assert row.password == "test2"

    cmd = buildCmd(session, GetUser, {"username": "test2"}, "admin")
    resp = checkResp(cmd.req, cmd())
    user = resp.find("{http://subsonic.org/restapi}user")
    assert user.get("email") == ""

    cmd = buildCmd(session, UpdateUser,
                   {"username": "test2", "password": "test2",
                    "email": "test2@unsonic.org"}, "admin")
    checkResp(cmd.req, cmd())
    row = session.query(User).filter(User.name == "test2").one_or_none()
    assert row.password == "test2"

    cmd = buildCmd(session, GetUser, {"username": "test2"}, "admin")
    resp = checkResp(cmd.req, cmd())
    user = resp.find("{http://subsonic.org/restapi}user")
    assert user.get("email") == "test2@unsonic.org"
