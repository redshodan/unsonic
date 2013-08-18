from __future__ import print_function

import os, sys, argparse

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from pyramid.security import forget
from pyramid.view import forbidden_view_config

import unsonic
from unsonic import models


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
        if not user.password:
            return
        if user and password == user.password:
            # Stash the user for easy access
            req.authed_user = user.export()
            return req.authed_user.roles


def init(global_config, config):
    authn_policy = SubsonicAuth(realm=unsonic.NAME)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    
