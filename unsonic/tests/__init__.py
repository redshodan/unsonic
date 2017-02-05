import os, shutil, unittest
from pathlib import Path

from pyramid import testing

from .. import __main__, web
from ..models import Session


class TestCase(unittest.TestCase):
    def setUp(self):
        setUpModule()
        shutil.copyfile("build/testing.sqlite.org", "build/testing.sqlite")
        self.config = testing.setUp()
        self.settings = self.config.get_settings()
        here = "/".join(os.path.dirname(__file__).split("/")[:-2])
        global_settings = {"__file__": os.path.join(here, "testing.ini"),
                           "here": here}
        web.init(global_settings, self.settings)
        super().setUp()


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
