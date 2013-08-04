import os, sys, argparse

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from .views import rest


from mishmash.commands import makeCmdLineParser

from .models import DBSession, Base
from . import db


def initMash():
    makeCmdLineParser()

def loadMash(settings):
    return db.loadMash(settings)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # Setup mishmash
    initMash()
    mash_settings = get_appsettings(global_config["__file__"], name="mishmash")
    mash_db = loadMash(mash_settings)

    # Pyramid framework
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()

    # Add the rest interfaces
    for cmd in rest.commands.itervalues():
        cmd.mash_db = mash_db
        cmd.mash_settings = mash_settings
        config.add_route(cmd.name, "/rest/" + cmd.name)
        config.add_view(cmd, route_name=cmd.name)

    app = config.make_wsgi_app()
    # Log requests
    return TransLogger(app, setup_console_handler=False)


### Logic for the unsonic-db tool. Located here for testing.
def doInit(settings, mash_settings):
    db.initPyramid(settings)
    db.initMash(mash_settings)

def doSync(settings, mash_settings):
    db.syncMash(mash_settings)

def buildParser():
    parser = argparse.ArgumentParser(prog="unsonic-db")
    subparsers = parser.add_subparsers()

    # Init
    init = subparsers.add_parser("init", help="Initiliaze the databases")
    init.add_argument("config", nargs=1, help="Configuration file")
    init.set_defaults(func=doInit)

    # Sync
    sync = subparsers.add_parser("sync", help="Synchronize the music database")
    sync.add_argument("config", nargs=1, help="Configuration file")
    sync.set_defaults(func=doSync)

    return parser

def dbMain(argv=sys.argv[1:]):
    parser = buildParser()
    args = parser.parse_args(args=argv)

    setup_logging(args.config[0])
    settings = get_appsettings(args.config[0])
    mash_settings = get_appsettings(args.config[0], name="mishmash")

    initMash()
    args.func(settings, mash_settings)
