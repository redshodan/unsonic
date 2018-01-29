import os
import uuid
import pytest
from pathlib import Path
from collections import namedtuple
from pyramid import testing
from sqlalchemy import create_engine
import mishmash

from unsonic import __main__, web, models, auth
from unsonic.config import CONFIG


DatabaseInfo = namedtuple("TestDatabase", ["url", "engine", "SessionMaker",
                                           "connection", "type"])


PSQL_KILL = \
"""SELECT pg_terminate_backend(pg_stat_activity.pid)
   FROM pg_stat_activity
   WHERE pg_stat_activity.datname = '%s'
     AND pid <> pg_backend_pid();"""


def bootstrap(dbinfo):
    # Initialize the db layer
    config = testing.setUp()
    settings = config.get_settings()
    here = "/".join(os.path.dirname(__file__).split("/")[:-2])
    global_settings = {"__file__": os.path.join(here, "test/testing.ini"),
                       "here": here, "venv":CONFIG.venv()}
    web.init(global_settings, settings, dbinfo)

    # Sync the database with mishmash
    __main__.main(["-D", dbinfo.url, "-c", "test/testing.ini", "sync"])

    # Create test users
    session = dbinfo.SessionMaker()
    user = models.addUser(session, "test", "test", auth.Roles.def_user_roles)
    user.avatar = 3
    session.add(user)
    session.commit()
    session.close()

    # Load the users
    models.load()


@pytest.fixture(scope="session", params=["sqlite", "postgresql"])
def database(request):
    if request.param == "sqlite":
        topdir = "/".join(os.path.dirname(__file__).split("/")[:-2])
        dbname = os.path.abspath(os.path.join(CONFIG.venv(), "testing.sqlite"))
        db = Path(dbname)
        if db.exists():
            db.unlink()
        db_url = f"sqlite:///{dbname}"
    elif request.param == "postgresql":
        uid = str(uuid.uuid4())
        uid = uid.replace("-", "")
        dbname = f"untest_{uid}"
        db_url = f"postgresql:///{dbname}"
    else:
        assert not("unhandled db: " + request.param)

    engine, SessionMaker, connection = mishmash.database.init(db_url)

    trans = connection.begin()
    dbinfo = DatabaseInfo(url=db_url, engine=engine, SessionMaker=SessionMaker,
                          connection=connection, type=request.param)
    bootstrap(dbinfo)
    yield dbinfo
    trans.rollback()

    # Clean up the databases
    if request.param == "sqlite":
        connection.close()
        engine.dispose()
        db = Path(dbname)
        if db.exists():
            db.unlink()
    elif (request.param == "postgresql" and
          "UN_TEST_NO_CLEANUP" not in os.environ):
        # Clean up dangling connections
        connection.execute(PSQL_KILL % dbname)
        connection.close()
        engine.dispose()
        # Connect to another database and drop the used one
        engine = create_engine("postgresql:///template1")
        conn = engine.connect()
        conn.connection.set_isolation_level(0)
        conn.execute(f"DROP DATABASE {dbname};")
        conn.close()


@pytest.fixture()
def session(database):
    session = database.SessionMaker()
    session.database = database
    yield session
    session.rollback()
    session.close()
