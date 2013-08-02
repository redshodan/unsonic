from __future__ import print_function

import os, sys, transaction

import mishmash
from mishmash.commands import Command
from mishmash.database import DBInfo, Database

from pyramid.settings import aslist

from sqlalchemy import engine_from_config

from ..models import DBSession, MyModel, Base


def asdict(value):
    ret = {}
    for line in [x.strip() for x in value.splitlines()]:
        if len(line):
            key, val = line.split(":")
            ret[key.strip()] = val.strip()
    return ret

# Setup the pyramid database
def initPyramid(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)

def initMash(settings):
    dbinfo = DBInfo(uri=settings["sqlalchemy.url"])
    Command.cmds["init"].run(dbinfo)

def syncMash(settings):
    dbinfo = DBInfo(uri=settings["sqlalchemy.url"])
    paths = [os.path.expandvars(os.path.expanduser(v)) for v in getMashPaths(settings).itervalues()]
    Command.cmds["sync"].run(dbinfo, paths)

def getMashPaths(settings):
    return asdict(settings["music.paths"])
    
def loadMash(settings):
    return Database(DBInfo(uri=settings["sqlalchemy.url"]))
