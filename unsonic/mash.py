from __future__ import print_function

import os

import mishmash
from mishmash.commands import Command, makeCmdLineParser
from mishmash.database import DBInfo, Database

from .models import DBSession


def asdict(value):
    ret = {}
    for line in [x.strip() for x in value.splitlines()]:
        if len(line):
            key, val = line.split(":")
            ret[key.strip()] = val.strip()
    return ret

def init(settings):
    makeCmdLineParser()

def initDB(settings):
    dbinfo = DBInfo(uri=settings["sqlalchemy.url"],
                    dbengine=DBSession.get_bind(),
                    dbsession=DBSession)
    Command.cmds["init"].run(dbinfo)

def syncDB(settings):
    dbinfo = DBInfo(uri=settings["sqlalchemy.url"],
                    dbengine=DBSession.get_bind(),
                    dbsession=DBSession)
    paths = [v for v in getPaths(settings).itervalues()]
    Command.cmds["sync"].run(dbinfo, paths)

def getPaths(settings):
    paths = asdict(settings["mishmash.paths"])
    for key in paths.keys():
        paths[key] = os.path.expandvars(os.path.expanduser(paths[key]))
    return paths
    
def load(settings):
    return Database(DBInfo(uri=settings["sqlalchemy.url"],
                           dbengine=DBSession.get_bind(),
                           dbsession=DBSession))
