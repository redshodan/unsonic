import os, unittest, transaction

from pyramid import testing

from .. import dbMain
from ..models import Session, Base, User, Role


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
            
        dbMain(["-c", "testing.ini", "init"])


    def testDBSync(self):
        self.testDBInit()
        
        dbMain(["-c", "testing.ini", "sync"])


    def testAddUser(self):
        self.testDBInit()
        ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass",
                      "role1", "role2"])
        self.assertEqual(ret, 0)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].name, "sue")
        self.assertEqual(row[0].password, "pass")
        self.assertEqual(row[0].roles[0].name, "role1")
        self.assertEqual(row[0].roles[1].name, "role2")


    def testAddUserTwice(self):
        self.testDBInit()
        ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass",
                      "role1", "role2"])
        self.assertEqual(ret, 0)
        ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass",
                      "role1", "role2"])
        self.assertEqual(ret, -1)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].name, "sue")
        self.assertEqual(row[0].password, "pass")
        self.assertEqual(row[0].roles[0].name, "role1")
        self.assertEqual(row[0].roles[1].name, "role2")

            
    def testDelUser(self):
        self.testDBInit()
        ret = dbMain(["-c", "testing.ini", "adduser", "sue", "pass",
                      "role1", "role2"])
        self.assertEqual(ret, 0)
        ret = dbMain(["-c", "testing.ini", "deluser", "sue"])
        self.assertEqual(ret, 0)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
        self.assertEqual(len(row), 0)
