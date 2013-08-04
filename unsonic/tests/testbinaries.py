import os, unittest, transaction

from pyramid import testing

from .. import dbMain
from ..models import DBSession, Base


class TestBinaries(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def testDBInit(self):
        try:
            os.unlink("build/testing.sqlite")
        except OSError, e:
            if e.errno != 2:
                raise
        try:
            os.unlink("build/testing-mishmash.sqlite")
        except OSError, e:
            if e.errno != 2:
                raise
        try:
            dbMain(["init", "testing.ini"])
        finally:
            DBSession.remove()

    def testDBSync(self):
        self.testDBInit()
        try:
            dbMain(["sync", "testing.ini"])
        finally:
            DBSession.remove()
