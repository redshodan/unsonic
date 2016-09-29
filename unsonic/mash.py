import os
from argparse import Namespace

import mishmash
from mishmash.commands.command import Command
from mishmash.commands.sync import SyncPlugin
from mishmash.database import init as dbinit
from eyed3.main import main as eyed3_main


def asdict(value):
    ret = {}
    for line in [x.strip() for x in value.splitlines()]:
        if len(line):
            key, val = line.split(":")
            ret[key.strip()] = val.strip()
    return ret

### FIXME: This is pretty bad. Make it mo' nice.
sync_plugin = None

def setupSync(subparsers):
    global sync_plugin
    parser = subparsers.add_parser("sync", help="Synchronize the music database")
    parser.set_defaults(func=syncDB)
    sync_plugin = SyncPlugin(parser) 

def syncDB(args, settings):
    args.plugin = sync_plugin
    args.paths = [v for v in getPaths(settings).values()]
    args.db_engine, args.db_session = dbinit(mashConfig(settings))
    args.db_session = args.db_session()
    try:
        retval = eyed3_main(args, None)
        args.db_session.commit()
    except:
        args.db_session.rollback()
        raise
    finally:
        args.db_session.close()
    return retval

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
