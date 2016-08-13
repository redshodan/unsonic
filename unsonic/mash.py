

import os
from argparse import Namespace

import mishmash
from mishmash.commands.command import Command
from mishmash.database import init as dbinit
from eyed3.main import makeCmdLineParser

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
    cmd = Command.cmds["init"]
    cmd.db_engine, cmd.db_session = dbinit(settings["sqlalchemy.url"])
    cmd._run()

def syncDB(settings):
    paths = [v for v in getPaths(settings).values()]
    cmd = Command.cmds["sync"]
    cmd.db_engine, cmd.db_session = dbinit(settings["sqlalchemy.url"])
    cmd._run(paths=paths)

def getPaths(settings):
    paths = asdict(settings["mishmash.paths"])
    for key in list(paths.keys()):
        paths[key] = os.path.expandvars(os.path.expanduser(paths[key]))
    return paths
