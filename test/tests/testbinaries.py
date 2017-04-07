from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from unsonic import __main__
from unsonic.models import User


@pytest.fixture()
def lsession():
    db = Path("build/testing2.sqlite")
    if db.exists():
        db.unlink()

    engine = create_engine("sqlite:///build/testing2.sqlite")
    connection = engine.connect()
    SessionMaker = sessionmaker(bind=engine)

    session = SessionMaker()
    yield session
    session.close()
    connection.close()

    db = Path("build/testing2.sqlite")
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
