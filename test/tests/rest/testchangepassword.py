from unsonic.models import User
from unsonic.views.rest.changepassword import ChangePassword
from unsonic.views.rest import Command
from . import buildCmd, checkResp


def testChangePassword(session, ptesting):
    row = session.query(User).filter(User.name == "test").one_or_none()
    assert row.password == "test"
    cmd = buildCmd(session, ChangePassword,
                   {"username": "test", "password": "newpass"})
    checkResp(cmd.req, cmd())
    row = session.query(User).filter(User.name == "test").one_or_none()
    assert row.password == "newpass"


def testChangeSelfPassword(session, ptesting):
    cmd = buildCmd(session, ChangePassword, {"password": "newpass"})
    checkResp(cmd.req, cmd())
    row = session.query(User).filter(User.name == "test").one_or_none()
    assert row.password == "newpass"


def testChangeOtherPasswordNonAdmin(session, ptesting):
    cmd = buildCmd(session, ChangePassword, {"username": "admin",
                                             "password": "newpass"})
    checkResp(cmd.req, cmd(), Command.E_PERM)
    row = session.query(User).filter(User.name == "admin").one_or_none()
    assert row.password is None


def testChangeOtherPasswordAdmin(session, ptesting):
    cmd = buildCmd(session, ChangePassword, {"username": "test",
                                             "password": "newpass"}, "admin")
    checkResp(cmd.req, cmd())
    row = session.query(User).filter(User.name == "admin").one_or_none()
    assert row.password is None
    row = session.query(User).filter(User.name == "test").one_or_none()
    assert row.password == "newpass"
