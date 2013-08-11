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


from . import mash, models
from .views import rest


NAME = "Unsonic"


# Causes auth challenges to be sent back
@forbidden_view_config()
def forbidden_view(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


# Support the silly original auth scheme that Subsonic has
class SubsonicAuth(BasicAuthAuthenticationPolicy):
    def __init__(self, realm='Realm', debug=False):
        super(SubsonicAuth, self).__init__(
            self.authCheck, realm=realm, debug=debug)

    def unauthenticated_userid(self, request):
        if request.headers.get('Authorization'):
            return super(SubsonicAuth, self).unauthenticated_userid(request)
        elif ("u" not in request.params.keys() or
              "p" not in request.params.keys()):
            return None
        else:
            return request.params["u"]

    def callback(self, username, request):
        if request.headers.get('Authorization'):
            return super(SubsonicAuth, self).callback(username, request)
        elif ("u" not in request.params.keys() or
              "p" not in request.params.keys()):
            return None
        else:
            return self.check(request.params["u"], request.params["p"],
                              request)

    # Shared between both auth schemes
    def authCheck(self, username, password, req):
        user = models.getUserByName(username)
        if password == user.password:
            # Stash the user for easy access
            req.authed_user = user.export()
            return req.authed_user.groups


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

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

    authn_policy = SubsonicAuth(realm=NAME)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    
    # Add the rest interfaces
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
    for group in ["rest", "users"]:
        if group not in args.groups:
            args.groups.append(group)
    ret = models.addUser(args.username[0], args.password[0], args.groups)
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
    init = subparsers.add_parser("init", help="Initialize the databases")
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

    mash.init(settings)
    models.init(settings, False)
    return args.func(args, settings)
