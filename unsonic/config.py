import os
import logging
import configparser


# This needs to be very early in the import sequence so the monkeypatch
# works right.
import mishmash
from mishmash.config import Config as MishConfig

from unsonic import HERE, INSTALL, lastfm


log = logging.getLogger(__name__)


CONFIG = None
DEF_LOCS = [
    # Production paths
    "/etc/unsonic.ini",
    os.path.join(INSTALL, "etc", "unsonic.ini"),
    os.path.join(HERE, "var", "unsonic.ini"),
    os.path.join(HERE, "unsonic.ini"),
    # Dev paths
    os.path.join(HERE, "development.ini"),
    os.path.join(HERE, "unsonic", "etc", "development.ini")
]


# Config keys
DESC = "desc"
DEFAULT = "default"
SETTER = "setter"
VALUES = "values"

CFG_KEYS = {
    "art.prefer_lastfm": {DESC: "Prefer artwork from LastFM over local images.",
                          DEFAULT: False},
    "art.never_lastfm": {DESC: ("Never get artwork from LastFM when there are "
                                "no local images."), DEFAULT: False},
}
CFG_DESCS = {k: v[DESC] for k, v in CFG_KEYS.items()}

USER_CFG_KEYS = {
    "art.prefer_lastfm": {DESC: "Prefer artwork from LastFM over local images.",
                          DEFAULT: False},
    "art.never_lastfm": {DESC: ("Never get artwork from LastFM when there are "
                                "no local images."), DEFAULT: False},

    "lastfm.user": {DESC: "Username for your LastFM account"},
    "lastfm.password": {DESC: "Hashed password for your LastFM account",
                        SETTER: lambda v: lastfm.hashPassword(v)},
    "lastfm.lang": {DESC: "Language for LastFM queries",
                    DEFAULT: "english",
                    VALUES: lastfm.LANGUAGES},
}
USER_CFG_DESCS = {k: v[DESC] for k, v in USER_CFG_KEYS.items()}
USER_CFG_DEFS = {
    k: v[DEFAULT] if DEFAULT in v else None for k, v in USER_CFG_KEYS.items()}


class ConfigException(Exception):
    pass


class HereConfig(MishConfig):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        global CONFIG
        CONFIG = self
        # %(install)s
        self.set(configparser.DEFAULTSECT, "install", INSTALL)
        # %(here)s
        if filename:
            here = os.path.dirname(os.path.abspath(filename))
            self.set(configparser.DEFAULTSECT, "here", here)
        else:
            self.set(configparser.DEFAULTSECT, "here", INSTALL)
        # %(venv)s
        if "VIRTUAL_ENV" in os.environ:
            self.set(configparser.DEFAULTSECT, "venv",
                     os.path.abspath(os.environ["VIRTUAL_ENV"]))
        else:
            self.set(configparser.DEFAULTSECT, "venv",
                     os.path.abspath("venv"))

    def get(self, section, key, **kwargs):
        val = super().get(section, key, **kwargs)
        if val and "%(here)s" in val:
            return collapseRelativePaths(
                val.replace("%(here)s", super().get(configparser.DEFAULTSECT,
                                                    "here")))
        elif val and "%(install)s" in val:
            return collapseRelativePaths(
                val.replace("%(install)s", super().get(configparser.DEFAULTSECT,
                                                       "install")))
        elif val and "%(venv)s" in val:
            return collapseRelativePaths(
                val.replace("%(venv)s", super().get(configparser.DEFAULTSECT,
                                                    "venv")))
        else:
            return val

    def here(self):
        return self.get(configparser.DEFAULTSECT, "here")

    def install(self):
        return self.get(configparser.DEFAULTSECT, "install")

    def venv(self):
        return self.get(configparser.DEFAULTSECT, "venv")

    # TODO: Refactor these db values with the uber config

    def checkValue(self, key, val=None, username=None):
        if username:
            if key not in USER_CFG_KEYS:
                raise ConfigException(f"Invalid user config key: {key}")
            else:
                def_ = USER_CFG_KEYS[key]
        else:
            if key not in CFG_KEYS:
                raise ConfigException(f"Invalid global config key: {key}")
            else:
                def_ = USER_CFG_KEYS[key]
        if val and VALUES in def_:
            if val not in def_[VALUES]:
                raise ConfigException(
                    f"Invalid value '{val}' for key '{key}'. Must be one of: " +
                    ", ".join(def_[VALUES]))

    def setDbValue(self, session, key, val, username=None):
        from unsonic import models
        self.checkValue(key, val=val, username=username)
        if username:
            if SETTER in USER_CFG_KEYS[key]:
                val = USER_CFG_KEYS[key][SETTER](val)
            return models.setUserConfig(session, username, key, val)
        else:
            return models.setGlobalConfig(session, key, val)

    def getDbValue(self, session, key=None, username=None):
        from unsonic import models
        if not key:
            if username:
                return models.getUserConfig(session, username)
            else:
                return models.getGlobalConfig(session)
        else:
            self.checkValue(key, username=username)
            if username:
                val = models.getUserConfig(session, username, key=key)
                if not val and DEFAULT in USER_CFG_KEYS[key]:
                    return models.UserConfig(key=key,
                                             value=USER_CFG_KEYS[key][DEFAULT])
            else:
                val = models.getGlobalConfig(session, key=key)
                if not val and DEFAULT in CFG_KEYS[key]:
                    return models.UserConfig(key=key,
                                             value=CFG_KEYS[key][DEFAULT])
            return val

    def delDbValue(self, session, key, username=None):
        from unsonic import models
        if username:
            return models.delUserConfig(session, username, key=key)
        else:
            return models.delGlobalConfig(session, key=key)

    def getDbValueKeys(self):
        return CFG_DESCS

    def getDbValueUserKeys(self):
        return USER_CFG_DESCS

    def getDbValueUserDefaults(self):
        return USER_CFG_DEFS


def collapseRelativePaths(path):
    output = []
    skip = 0
    bits = path.split("/")
    bits.reverse()
    for bit in bits:
        if bit == "..":
            skip += 1
        else:
            if skip > 0:
                skip -= 1
                continue
            else:
                output.append(bit)
    output.reverse()
    return "/".join(output)


# Try to find a standard config file if not specified on the cmdline
def findConfig(parser, args):
    args, unknown = parser.parse_known_args(args)
    if args.config is not parser.get_default("config"):
        log.debug("Using user specified config file")
        return True

    for path in DEF_LOCS:
        if os.path.isfile(path):
            log.debug("No config specified, found config file: " +
                      os.path.abspath(path))
            return path
    else:
        return False
