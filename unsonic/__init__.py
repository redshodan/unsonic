from __future__ import print_function

import os, sys, argparse

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.paster import get_appsettings, setup_logging
from pyramid.view import view_config, forbidden_view_config


from . import mash, models, log, auth
from .views import rest


NAME = "Unsonic"


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # log.setupMash()
    
    # Setup models
    models.init(settings, True)
    
    # Setup mishmash
    mash.load(settings)

    # Pyramid framework
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600,)
    config.add_route('home', '/', factory="unsonic.views.RouteContext")
    config.scan()

    global NAME
    if "unsonic.name" in settings:
        NAME = settings["unsonic.name"]

    # Init auth
    auth.init(global_config, config)

    # Init jamstash
    jamstash.init(global_config, config)

    # Add the rest interfaces
    config.add_route("rest", "/rest", factory="unsonic.views.rest.RouteContext")
    for cmd in rest.commands.itervalues():
        cmd.settings = settings
        config.add_route(cmd.name, "/rest/" + cmd.name,
                         factory="unsonic.views.rest.RouteContext")
        config.add_view(cmd, route_name=cmd.name, permission="rest")

    # Log requests
    app = config.make_wsgi_app()
    return TransLogger(app, setup_console_handler=False)


### Logic for the unsonic-db tool. Located here for testing.
def doInit(args, settings):
    models.initDB(settings)
    return 0

def doSync(args, settings):
    mash.syncDB(settings)
    return 0

def doAddUser(args, settings):
    print("Adding user '%s'.." % args.username[0])
    for role in ["rest", "users"]:
        if role not in args.roles:
            args.roles.append(role)
    ret = models.addUser(args.username[0], args.password[0], args.roles)
    if ret is True:
        print("Added.")
        return 0
    else:
        print(ret)
        return -1

def doDelUser(args, settings):
    print("Deleting user '%s'" % args.username[0])
    models.delUser(args.username[0])
    print("Deleted.")
    return 0

def doListUsers(args, settings):
    print("Users:")
    for user in models.DBSession.query(models.User).all():
        roles = [g.name for g in user.roles]
        print("   %s:  roles: %s" % (user.name, ", ".join(roles)))
    return 0
    
def buildParser():
    parser = argparse.ArgumentParser(prog="unsonic-db")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-c", "--config", required=True,
                          help="Configuration file")
    subparsers = parser.add_subparsers(title="commands")

    # Init
    init = subparsers.add_parser("init", help="Initialize the databases")
    init.set_defaults(func=doInit)

    # Sync
    sync = subparsers.add_parser("sync", help="Synchronize the music database")
    sync.set_defaults(func=doSync)

    # Adduser
    adduser = subparsers.add_parser("adduser", help="Add a user to the database")
    adduser.add_argument("username", nargs=1, help="Username")
    adduser.add_argument("password", nargs=1, help="Password")
    adduser.add_argument("roles", nargs=argparse.REMAINDER,
                         help="Roles for the user")
    adduser.set_defaults(func=doAddUser)

    # deluser
    deluser = subparsers.add_parser("deluser",
                                    help="Delete a user from the database")
    deluser.add_argument("username", nargs=1, help="Username")
    deluser.set_defaults(func=doDelUser)

    # listusers
    deluser = subparsers.add_parser("listusers",
                                    help="List users in the database")
    deluser.set_defaults(func=doListUsers)

    return parser

def dbMain(argv=sys.argv[1:]):
    parser = buildParser()
    args = parser.parse_args(args=argv)

    setup_logging(args.config)
    settings = get_appsettings(args.config)

    # log.setupMash()
    mash.init(settings)
    models.init(settings, False)
    return args.func(args, settings)
