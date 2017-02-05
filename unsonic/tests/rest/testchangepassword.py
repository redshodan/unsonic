import unittest

from pyramid import testing

from . import RestTestCase
from ...models import Session, User
from ...views.rest.changepassword import ChangePassword
from ...views.rest import Command


class TestChangePassword(RestTestCase):
    def testChangePassword(self):
        with Session() as session:
            row = session.query(User).filter(User.name == "test").one_or_none()
            self.assertEqual(row.password, "test")
        cmd = self.buildCmd(ChangePassword,
                            {"username": "test", "password": "newpass"})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        with Session() as session:
            row = session.query(User).filter(User.name == "test").one_or_none()
            self.assertEqual(row.password, "newpass")


    def testChangeSelfPassword(self):
        cmd = self.buildCmd(ChangePassword, {"password": "newpass"})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        with Session() as session:
            row = session.query(User).filter(User.name == "test").one_or_none()
            self.assertEqual(row.password, "newpass")


    def testChangeOtherPasswordNonAdmin(self):
        cmd = self.buildCmd(ChangePassword, {"username": "admin",
                                             "password": "newpass"})
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp, Command.E_PERM)
        with Session() as session:
            row = session.query(User).filter(User.name == "admin").one_or_none()
            self.assertEqual(row.password, None)


    def testChangeOtherPasswordAdmin(self):
        cmd = self.buildCmd(ChangePassword, {"username": "test",
                                             "password": "newpass"}, "admin")
        resp = cmd()
        sub_resp = self.checkResp(cmd.req, resp)
        with Session() as session:
            row = session.query(User).filter(User.name == "admin").one_or_none()
            self.assertEqual(row.password, None)
            row = session.query(User).filter(User.name == "test").one_or_none()
            self.assertEqual(row.password, "newpass")
            
