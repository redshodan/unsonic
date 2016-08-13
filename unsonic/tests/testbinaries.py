import os, unittest, transaction

from pyramid import testing

from .. import dbMain
from ..models import DBSession, Base, User, Role


class TestBinaries(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def testDBInit(self):
        try:
            os.unlink("build/testing.sqlite")
        except OSError as e:
            if e.errno != 2:
                raise
        try:
            os.unlink("build/testing-mishmash.sqlite")
        except OSError as e:
            if e.errno != 2:
                raise
        try:
            dbMain(["-c", "testing.ini", "init"])
        finally:
            DBSession.remove()

    def testDBSync(self):
        self.testDBInit()
        try:
            dbMain(["-c", "testing.ini", "sync"])
        finally:
            DBSession.remove()

    def testAddUser(self):
        self.testDBInit()
        try:
            ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass", "role1", "role2"])
            self.assertEqual(ret, 0)
            row = DBSession.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 1)
            self.assertEqual(row[0].name, "sue")
            self.assertEqual(row[0].password, "pass")
            self.assertEqual(row[0].roles[0].name, "role1")
            self.assertEqual(row[0].roles[1].name, "role2")
        finally:
            DBSession.remove()

    def testAddUserTwice(self):
        self.testDBInit()
        try:
            ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass", "role1", "role2"])
            DBSession.remove()
            self.assertEqual(ret, 0)
            ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass", "role1", "role2"])
            self.assertEqual(ret, -1)
            row = DBSession.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 1)
            self.assertEqual(row[0].name, "sue")
            self.assertEqual(row[0].password, "pass")
            self.assertEqual(row[0].roles[0].name, "role1")
            self.assertEqual(row[0].roles[1].name, "role2")
        finally:
            DBSession.remove()
            
    def testDelUser(self):
        self.testDBInit()
        try:
            ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass", "role1", "role2"])
            DBSession.remove()
            self.assertEqual(ret, 0)
            ret = dbMain(["-c", "testing.ini", "deluser", "sue"])
            self.assertEqual(ret, 0)
            row = DBSession.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 0)
        finally:
            DBSession.remove()
            
