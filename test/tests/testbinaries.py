import sys
import os
from pathlib import Path
import pytest
from pyramid import testing

from unsonic import __main__, web, models
from unsonic.config import CONFIG, CFG_KEYS, USER_CFG_KEYS
from unsonic.models import User, Config, UserConfig


# Inject some test config key names
CFG_KEYS["test1"] = "Test key"
USER_CFG_KEYS["test1"] = "Test key"


@pytest.fixture()
def lsession():
    db = Path(os.path.join(CONFIG.venv(), "testing2.sqlite"))
    if db.exists():
        db.unlink()

    config = testing.setUp()
    settings = config.get_settings()
    here = "/".join(os.path.dirname(__file__).split("/")[:-2])
    global_settings = {"__file__": os.path.join(here, "test/testing2.ini"),
                       "here": here,  "venv": CONFIG.venv()}
    web.init(global_settings, settings, None)

    session = models.session_maker()
    yield session
    session.close()

    db = Path(os.path.join(CONFIG.venv(), "testing2.sqlite"))
    db.unlink()


def testAddUser(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "adduser", "sue", "pass",
                "role1", "role2"]
    ret = __main__.main()
    assert ret == 0
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 1
    assert row[0].name == "sue"
    assert row[0].password == "pass"
    roles = [r.name for r in row[0].roles]
    assert "role1" in roles
    assert "role2" in roles


def testAddUserTwice(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "adduser", "sue", "pass",
                "role1", "role2"]
    ret = __main__.main()
    assert ret == 0
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "adduser", "sue", "pass",
                "role1", "role2"]
    ret = __main__.main()
    assert ret == -1
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 1
    assert row[0].name == "sue"
    assert row[0].password == "pass"
    roles = [r.name for r in row[0].roles]
    assert "role1" in roles
    assert "role2" in roles


def testDelUser(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "adduser", "sue", "pass", "role1",
                "role2"]
    ret = __main__.main()
    assert ret == 0
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "deluser", "sue"]
    ret = __main__.main()
    assert ret == 0
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 0


def testPassword(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "adduser", "sue", "pass",
                "role1", "role2"]
    ret = __main__.main()
    assert ret == 0
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "password", "sue",
                "testtest"]
    ret = __main__.main()
    assert ret == 0
    row = lsession.query(User).filter(User.name == "sue").all()
    assert len(row) == 1
    assert row[0].password == "testtest"


def testConfigSetGlobal(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "config",
                "-s", "test1=val1"]
    ret = __main__.main()
    assert ret == 0
    row = lsession.query(Config).filter(Config.key == "test1").all()
    assert len(row) == 1
    assert row[0].key == "test1"
    assert row[0].value == "val1"
    assert row[0].modified is not None


def testConfigSetGlobalBadKey(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "config",
                "-s", "badkey=val1"]
    ret = __main__.main()
    assert ret != 0
    row = lsession.query(Config).filter(Config.key == "badkey").all()
    assert len(row) == 0


def testConfigGetGlobal(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "config",
                "-s", "test1=val1"]
    ret = __main__.main()
    assert ret == 0
    row = lsession.query(Config).filter(Config.key == "test1").all()
    assert len(row) == 1
    assert row[0].key == "test1"
    assert row[0].value == "val1"
    assert row[0].modified is not None

    sys.argv = ["unsonic", "-c", "test/testing2.ini", "config",
                "-g", "test1"]
    ret = __main__.main()
    assert ret == 0


def testConfigGetGlobalMissing(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "config",
                "-g", "test1"]
    ret = __main__.main()
    assert ret != 0


def testConfigSetUser(lsession):
    sys.argv = ["unsonic", "-c", "test/testing2.ini", "adduser", "sue", "pass",
                "role1", "role2"]
    ret = __main__.main()
    assert ret == 0

    sys.argv = ["unsonic", "-c", "test/testing2.ini", "config",
                "-s", "test1=val1", "sue"]
    ret = __main__.main()
    assert ret == 0
    user = lsession.query(User).filter(User.name == "sue").one()
    row = lsession.query(UserConfig).filter(User.id == user.id,
                                            UserConfig.key == "test1").all()
    assert len(row) == 1
    assert row[0].user_id == user.id
    assert row[0].key == "test1"
    assert row[0].value == "val1"
    assert row[0].modified is not None
