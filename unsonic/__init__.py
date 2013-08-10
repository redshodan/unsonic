from __future__ import print_function

import os, sys, argparse

from paste.translogger import TransLogger
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from pyramid.paster import get_appsettings, setup_logging
from pyramid.security import forget
from pyramid.view import view_config, forbidden_view_config

from mishmash.commands import makeCmdLineParser

from . import mash, models
from .views import rest


NAME = "Unsonic"


# Causes auth challenges to be sent back
@forbidden_view_config()
def forbidden_view(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response

def authCheck(username, passwd, req):
    if username in models.users.keys():
        user = models.users[username]
        return user.groups

def initMash():
    makeCmdLineParser()

def loadMash(settings):
    return mash.load(settings)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # Setup mishmash
    initMash()
    mash_settings = get_appsettings(global_config["__file__"], name="mishmash")
    mash_db = loadMash(mash_settings)

    # Setup models
    models.init(settings)
    models.loadData()

    # Pyramid framework
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()

    global NAME
    if "unsonic.name" in settings:
        NAME = settings["unsonic.name"]

    authn_policy = BasicAuthAuthenticationPolicy(authCheck, realm=NAME,
                                                 debug=True)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    
    # Add the rest interfaces
    for cmd in rest.commands.itervalues():
        cmd.mash_db = mash_db
        cmd.mash_settings = mash_settings
        config.add_route(cmd.name, "/rest/" + cmd.name,
                         factory="unsonic.views.rest.RouteContext")
        config.add_view(cmd, route_name=cmd.name, permission="rest")

    # Log requests
    app = config.make_wsgi_app()
    return TransLogger(app, setup_console_handler=False)


### Logic for the unsonic-db tool. Located here for testing.
def doInit(args, settings, mash_settings):
    models.init(settings)
    models.initModels()
    mash.init(mash_settings)
    return 0

def doSync(args, settings, mash_settings):
    mash.sync(mash_settings)
    return 0

def doAddUser(args, settings, mash_settings):
    print("Adding user '%s'.." % args.username[0])
    if "rest" not in args.groups:
        args.groups.append("rest")
    ret = models.addUser(args.username[0], args.password[0], args.groups)
    if ret is True:
        print("Added.")
        return 0
    else:
        print(ret)
        return -1

def doDelUser(args, settings, mash_settings):
    print("Deleting user '%s'" % args.username[0])
    models.delUser(args.username[0])
    print("Deleted.")
    return 0

def doListUsers(args, settings, mash_settings):
    print("Users:")
    for user in models.DBSession.query(models.User).all():
        groups = [g.name for g in user.groups]
        print("   %s:  groups: %s" % (user.name, ", ".join(groups)))
    return 0
    
def buildParser():
    parser = argparse.ArgumentParser(prog="unsonic-db")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-c", "--config", required=True,
                          help="Configuration file")
    subparsers = parser.add_subparsers(title="commands")

    # Init
    init = subparsers.add_parser("init", help="Initiliaze the databases")
    init.set_defaults(func=doInit)

    # Sync
    sync = subparsers.add_parser("sync", help="Synchronize the music database")
    sync.set_defaults(func=doSync)

    # Adduser
    adduser = subparsers.add_parser("adduser", help="Add a user to the database")
    adduser.add_argument("username", nargs=1, help="Username")
    adduser.add_argument("password", nargs=1, help="Password")
    adduser.add_argument("groups", nargs=argparse.REMAINDER,
                         help="Groups for the user")
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
    mash_settings = get_appsettings(args.config, name="mishmash")

    models.init(settings)
    initMash()
    return args.func(args, settings, mash_settings)
