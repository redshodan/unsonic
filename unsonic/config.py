import os
import configparser
import logging


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
    os.path.join(INSTALL, "etc/unsonic.ini"),
    os.path.join(HERE, "unsonic.ini"),
    os.path.join(HERE, "unsonic.ini"),
    # Dev paths
    os.path.join(HERE, "development.ini"),
    os.path.join(HERE, "unsonic/etc/development.ini")
]


# Config keys
DESC = "desc"
SETTER = "setter"

CFG_KEYS = {
}
CFG_DESCS = {k: v[DESC] for k, v in CFG_KEYS.items()}

USER_CFG_KEYS = {
    "lastfm.user": {DESC: "Username for your LastFM account"},
    "lastfm.password": {DESC: "Hashed password for your LastFM account",
                        SETTER: lambda v: lastfm.hashPassword(v)},
}
USER_CFG_DESCS = {k: v[DESC] for k, v in USER_CFG_KEYS.items()}


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
        if username and key not in USER_CFG_KEYS:
            raise ConfigException(f"Invalid user config key: {key}")
        elif not username and key not in CFG_KEYS:
            raise ConfigException(f"Invalid global config key: {key}")

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
                return models.getUserConfig(session, username, key=key)
            else:
                return models.getGlobalConfig(session, key=key)

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


mishmash.config.Config = HereConfig


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
def findConfig(parser):
    args, unknown = parser.parse_known_args()
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
