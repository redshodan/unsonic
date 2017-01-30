import unittest
from pathlib import Path

from pyramid import testing

from .. import __main__
from ..models import Session


class TestCase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from ..models import Base
        # DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

    def tearDown(self):
        self.session.remove()
        self.session.close()
        testing.tearDown()


def setUpModule():
    if Path("build/testing.sqlite.org").exists():
        return

    print("\nSetting up test database...")

    # Build a fresh mishmash db
    db = Path("build/testing.sqlite")
    if db.exists():
        db.unlink()

    __main__.main(["-c", "testing.ini", "sync", "test/music"])
    __main__.main(["-c", "testing.ini", "adduser", "test", "test"])

    # Cache the fresh db for each test run to copy
    db.rename("build/testing.sqlite.org")

    print("Test setup complete\n")
