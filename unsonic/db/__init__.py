from __future__ import print_function

import os, sys, transaction

import mishmash
from mishmash.commands import Command
from mishmash.database import DBInfo

from pyramid.settings import aslist

from sqlalchemy import engine_from_config

from ..models import DBSession, MyModel, Base


# Setup the pyramid database
def initPyramid(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)

def initMishMash(settings):
    dbinfo = DBInfo(uri=settings["sqlalchemy.url"])
    Command.cmds["init"].run(dbinfo)

def syncMishMash(settings):
    dbinfo = DBInfo(uri=settings["sqlalchemy.url"])
    paths = []
    for path in aslist(settings["music.paths"]):
        paths.append(os.path.expanduser(path))
    Command.cmds["sync"].run(dbinfo, paths)
