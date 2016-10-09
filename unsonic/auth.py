import os, sys, argparse, hashlib

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from pyramid.security import forget
from pyramid.view import forbidden_view_config

import unsonic
from unsonic import models
from unsonic.models import Session


class User():
    def __init__(self, db_user):
        self.id = db_user.id
        self.name = db_user.name
        self.password = db_user.password
        self.email = db_user.email
        self.scrobbling = db_user.scrobbling
        self.roles = []
        for role in db_user.roles:
            self.roles.append(role.name)


    def isAdmin(self):
        return Roles.ADMIN in self.roles


    def isUser(self):
        return Roles.USERS in self.roles


    def isRest(self):
        return Roles.REST in self.roles


class Roles(object):
    # Pyramind roles
    ADMIN = "admin" # both pyramid and subsonic
    USERS = "users"
    REST = "rest"

    # Subsonic roles, includes admin role
    SETTINGS = "settings"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    PLAYLIST = "playlist"
    COVERART = "coverart"
    COMMENT = "comment"
    PODCAST = "podcast"
    STREAM = "stream"
    JUKEBOX = "jukebox"
    SHARE = "share"

    # Role groups
    subsonic_roles = [ADMIN, SETTINGS, DOWNLOAD, PLAYLIST, COVERART, COMMENT,
                      PODCAST, STREAM, JUKEBOX, SHARE]
    admin_roles = [ADMIN, USERS, REST, SETTINGS, DOWNLOAD, PLAYLIST, COVERART,
                   COMMENT, PODCAST, STREAM, JUKEBOX, SHARE]
    def_user_roles = [USERS, REST, DOWNLOAD, PLAYLIST, COVERART, COMMENT,
                      PODCAST, STREAM, SHARE]


# Causes auth challenges to be sent back
@forbidden_view_config()
def forbidden_view(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


# Support the silly auth schemes that Subsonic has
class SubsonicAuth(BasicAuthAuthenticationPolicy):
    def __init__(self, realm='Realm', debug=False):
        super(SubsonicAuth, self).__init__(
            self.authCheck, realm=realm, debug=debug)

    def unauthenticated_userid(self, request):
        if request.headers.get('Authorization'):
            return super(SubsonicAuth, self).unauthenticated_userid(request)
        elif ("u" not in list(request.params.keys()) or
              ("p" not in list(request.params.keys()) and
               "t" not in list(request.params.keys()) and
               "s" not in list(request.params.keys()))):
            return None
        else:
            return request.params["u"]

    def callback(self, username, request):
        if request.headers.get('Authorization'):
            return super(SubsonicAuth, self).callback(username, request)
        elif ("u" not in list(request.params.keys()) or
              ("p" not in list(request.params.keys()) and
               "t" not in list(request.params.keys()) and
               "s" not in list(request.params.keys()))):
            return None
        else:
            if "p" in list(request.params.keys()):
                password = request.params["p"]
            else:
                password = None
            return self.check(request.params["u"], password, request)

    # Shared between both auth schemes
    def authCheck(self, username, password, req):
        with Session() as session:
            user = models.getUserByName(session, username)
            if not user or user and not user.password:
                return
            if ("t" in list(req.params.keys()) and
                "s" in list(req.params.keys())):
                sum = hashlib.md5()
                sum.update(user.password.encode("utf-8"))
                sum.update(req.params["s"].encode("utf-8"))
                if sum.hexdigest() == req.params["t"]:
                    # Stash the user for easy access
                    req.authed_user = user.export()
                    return req.authed_user.roles
            if user and password == user.password:
                # Stash the user for easy access
                req.authed_user = user.export()
                return req.authed_user.roles


def init(global_config, config):
    authn_policy = SubsonicAuth(realm=unsonic.NAME)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
