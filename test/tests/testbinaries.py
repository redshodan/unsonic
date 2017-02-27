from unsonic import __main__
from unsonic.models import Session, User
from . import TestCase


class TestBinaries(TestCase):
    def testAddUser(self):
        ret = __main__.main(["-c", "test/testing.ini", "adduser", "sue", "pass",
                            "role1", "role2"])
        self.assertEqual(ret, 0)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 1)
            self.assertEqual(row[0].name, "sue")
            self.assertEqual(row[0].password, "pass")
            roles = [r.name for r in row[0].roles]
            self.assertTrue("role1" in roles)
            self.assertTrue("role2" in roles)


    def testAddUserTwice(self):
        ret = __main__.main(["-c", "test/testing.ini", "adduser", "sue", "pass",
                            "role1", "role2"])
        self.assertEqual(ret, 0)
        ret = __main__.main(["-c", "test/testing.ini", "adduser", "sue", "pass",
                            "role1", "role2"])
        self.assertEqual(ret, -1)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 1)
            self.assertEqual(row[0].name, "sue")
            self.assertEqual(row[0].password, "pass")
            roles = [r.name for r in row[0].roles]
            self.assertTrue("role1" in roles)
            self.assertTrue("role2" in roles)


    def testDelUser(self):
        ret = __main__.main(["-c", "test/testing.ini", "adduser", "sue", "pass",
                            "role1", "role2"])
        self.assertEqual(ret, 0)
        ret = __main__.main(["-c", "test/testing.ini", "deluser", "sue"])
        self.assertEqual(ret, 0)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 0)


    def testPassword(self):
        ret = __main__.main(["-c", "test/testing.ini", "adduser", "sue", "pass",
                            "role1", "role2"])
        self.assertEqual(ret, 0)
        ret = __main__.main(["-c", "test/testing.ini", "password", "sue",
                             "testtest"])
        self.assertEqual(ret, 0)
        with Session() as session:
            row = session.query(User).filter(User.name == "sue").all()
            self.assertEqual(len(row), 1)
            self.assertEqual(row[0].password, "testtest")
