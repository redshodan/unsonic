import os
from pathlib import Path
import pytest
from pyramid import testing

from unsonic import __main__, web, models
from unsonic.config import CONFIG
from unsonic.models import User


@pytest.fixture()
def lsession():
    db = Path(os.path.join(CONFIG.venv(), "testing2.sqlite"))
    if db.exists():
        db.unlink()

    config = testing.setUp()
    settings = config.get_settings()
    here = "/".join(os.path.dirname(__file__).split("/")[:-2])
    global_settings = {"__file__": os.path.join(here, "test/testing2.ini"),
                       "here": here,  "venv":CONFIG.venv()}
    web.init(global_settings, settings, None)

    session = models.session_maker()
    yield session
    session.close()

    db = Path(os.path.join(CONFIG.venv(), "testing2.sqlite"))
    db.unlink()


def testAddUser(lsession):
    ret = __main__.main(["-c", "test/testing2.ini", "adduser", "sue", "pass",
                         "role1", "role2"])
    assert ret == 0
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 1
    assert row[0].name == "sue"
    assert row[0].password == "pass"
    roles = [r.name for r in row[0].roles]
    assert "role1" in roles
    assert "role2" in roles


def testAddUserTwice(lsession):
    ret = __main__.main(["-c", "test/testing2.ini", "adduser", "sue", "pass",
                         "role1", "role2"])
    assert ret == 0
    ret = __main__.main(["-c", "test/testing2.ini", "adduser", "sue", "pass",
                         "role1", "role2"])
    assert ret == -1
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 1
    assert row[0].name == "sue"
    assert row[0].password == "pass"
    roles = [r.name for r in row[0].roles]
    assert "role1" in roles
    assert "role2" in roles


def testDelUser(lsession):
    ret = __main__.main(["-c", "test/testing2.ini", "adduser", "sue", "pass",
                         "role1", "role2"])
    assert ret == 0
    ret = __main__.main(["-c", "test/testing2.ini", "deluser", "sue"])
    assert ret == 0
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 0


def testPassword(lsession):
    ret = __main__.main(["-c", "test/testing2.ini", "adduser", "sue", "pass",
                         "role1", "role2"])
    assert ret == 0
    ret = __main__.main(["-c", "test/testing2.ini", "password", "sue",
                         "testtest"])
    assert ret == 0
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 1
    assert row[0].password == "testtest"
