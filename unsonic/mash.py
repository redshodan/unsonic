

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
    cmd = Command._all_commands["init"]
    cmd.db_engine, cmd.db_session = dbinit(settings["sqlalchemy.url"])
    config = Namespace()
    config.various_artists_name = settings["mishmash.various_artists_name"]
    cmd._run(config=config)

def syncDB(settings):
    paths = [v for v in getPaths(settings).values()]
    cmd = Command._all_commands["sync"]
    cmd.db_engine, cmd.db_session = dbinit(mashConfig(settings))
    config = Namespace()
    config.various_artists_name = settings["mishmash.various_artists_name"]
    cmd._run(paths=paths, config=config)

def getPaths(settings):
    paths = asdict(settings["mishmash.paths"])
    for key in list(paths.keys()):
        paths[key] = os.path.expandvars(os.path.expanduser(paths[key]))
    return paths

def mashConfig(settings):
    config = Namespace()
    config.db_url = settings["sqlalchemy.url"]
    config.various_artists_name = settings["mishmash.various_artists_name"]
    return config


