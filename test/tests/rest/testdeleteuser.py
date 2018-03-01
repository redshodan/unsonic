from unsonic.models import User
from unsonic.views.rest.createuser import CreateUser
from unsonic.views.rest.deleteuser import DeleteUser
from . import buildCmd, checkResp


def testCreateUser(session):
    cmd = buildCmd(session, CreateUser,
                   {"username": "test2", "password": "test2"}, "admin")
    checkResp(cmd.req, cmd())
    row = session.query(User).filter(User.name == "test2").one_or_none()
    assert row.password == "test2"

    cmd = buildCmd(session, DeleteUser, {"username": "test2"}, "admin")
    checkResp(cmd.req, cmd())

    row = session.query(User).filter(User.name == "test2").one_or_none()
    assert row is None
