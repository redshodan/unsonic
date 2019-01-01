import logging
import hashlib
import codecs
from functools import lru_cache

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import forget
from pyramid.view import forbidden_view_config

import unsonic
from unsonic import models, lastfm
from unsonic.models import Session

log = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def getUser(username):
    with Session() as session:
        return models.getUserByName(session, username)


class User():
    def __init__(self, db_user, db_user_config):
        self.id = db_user.id
        self.name = db_user.name
        self.password = db_user.password
        self.email = db_user.email
        self.scrobble_user = db_user.scrobble_user
        self.scrobble_pass = db_user.scrobble_pass
        self.scrobble_type = db_user.scrobble_type
        self.roles = []
        for role in db_user.roles:
            self.roles.append(role.name)
        self.avatar = db_user.avatar
        self.db_user_config = {u.key: u.value for u in db_user_config}
        self._lastfm = None
        self.listening = None
        self.folders = list([f for f in db_user.folders])

    def __getattr__(self, name):
        from .config import CONFIG
        mangled = name.replace("_", ".")
        if mangled in self.db_user_config:
            return self.db_user_config[mangled]
        elif mangled in CONFIG.getDbValueUserDefaults():
            return CONFIG.getDbValueUserDefaults()[mangled]
        else:
            raise AttributeError()

    @property
    def lastfm(self):
        if not self._lastfm:
            self._lastfm = lastfm.makeClient(self.lastfm_user,
                                             self.lastfm_password)
        return self._lastfm

    def isAdmin(self):
        return Roles.ADMIN in self.roles

    def isUser(self):
        return Roles.USERS in self.roles

    def isRest(self):
        return Roles.REST in self.roles

    def __repr__(self):
        msg = []
        for attr, val in self.__dict__.items():
            if not attr.startswith("_"):
                msg.append(f"{attr}: {val}")
        return "User(" + ", ".join(msg) + ")"


class Roles(object):
    # Pyramind roles
    #   ADMIN is for both pyramid and subsonic
    ADMIN = "admin"
    USERS = "users"
    REST = "rest"

    # Subsonic roles, includes admin role
    SETTINGS = "settings"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    PLAYLIST = "playlist"
    COVERART = "coverArt"
    COMMENT = "comment"
    PODCAST = "podcast"
    STREAM = "stream"
    JUKEBOX = "jukebox"
    SHARE = "share"
    VIDEOCONVERSION = "videoConversion"

    # Role groups
    subsonic_roles = [ADMIN, SETTINGS, DOWNLOAD, UPLOAD, PLAYLIST, COVERART,
                      COMMENT, PODCAST, STREAM, JUKEBOX, SHARE, VIDEOCONVERSION]
    admin_roles = [ADMIN, USERS, REST, SETTINGS, DOWNLOAD, PLAYLIST, COVERART,
                   COMMENT, PODCAST, STREAM, JUKEBOX, SHARE, VIDEOCONVERSION]
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
        super().__init__(self.authCheck, realm=realm, debug=debug)

    def unauthenticated_userid(self, request):
        if request.headers.get('Authorization'):
            return super().unauthenticated_userid(request)
        elif ("u" not in list(request.params.keys()) or
              ("p" not in list(request.params.keys()) and
               "t" not in list(request.params.keys()) and
               "s" not in list(request.params.keys()))):
            return None
        else:
            return request.params["u"]

    def callback(self, username, request):
        if request.headers.get('Authorization'):
            return super().callback(username, request)
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
        user = getUser(username)
        if not user or user and not user.password:
            log.warning(f"User {username} not found, or lacks a password")
            return
        if ("t" in list(req.params.keys()) and
                "s" in list(req.params.keys())):
            sum = hashlib.md5()
            sum.update(user.password.encode("utf-8"))
            sum.update(req.params["s"].encode("utf-8"))
            if sum.hexdigest() == req.params["t"]:
                # Stash the user for easy access
                req.authed_user = user
                return req.authed_user.roles
            else:
                return
        elif password.startswith("enc:"):
            try:
                decode_hex = codecs.getdecoder("hex_codec")
                password = decode_hex(password[4:])[0]
                password = password.decode("utf-8")
            except Exception as ex:
                log.warning(f"enc password decode error: {ex}")
                return
        if user and password == user.password:
            # Stash the user for easy access
            req.authed_user = user
            return req.authed_user.roles


def init(global_config, config):
    authn_policy = SubsonicAuth(realm=unsonic.web.NAME)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
