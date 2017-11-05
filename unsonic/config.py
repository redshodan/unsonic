import os
import configparser
import logging

# This needs to be very early in the import sequence so the monkeypatch
# works right.
import mishmash
from mishmash.config import Config as MishConfig

from unsonic import HERE, INSTALL


import nicfit
log = nicfit.getLogger(__name__)


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


class HereConfig(MishConfig):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        global CONFIG
        CONFIG = self
        # %(install)s
        self.set(configparser.DEFAULTSECT, "install", INSTALL)
        if filename:
            # %(here)s
            here = os.path.dirname(os.path.abspath(filename))
            self.set(configparser.DEFAULTSECT, "here", here)
        else:
            self.set(configparser.DEFAULTSECT, "here", INSTALL)


    def get(self, section, key, **kwargs):
        val = super().get(section, key, **kwargs)
        if val and "%(here)s" in val:
            return val.replace("%(here)s",
                               super().get(configparser.DEFAULTSECT, "here"))
        elif val and "%(install)s" in val:
            return val.replace("%(install)s",
                               super().get(configparser.DEFAULTSECT, "install"))
        else:
            return val


mishmash.config.Config = HereConfig


# Try to find a standard config file if not specified on the cmdline
def findConfig(parser):
    args, unknown = parser.parse_known_args()
    if args.config is not parser.get_default("config"):
        log.debug("Using user specified config file")
        return True

    for path in DEF_LOCS:
        if os.path.isfile(path):
            print("PATH", path)
            log.debug("No config specified, found config file: " +
                      os.path.abspath(path))
            return path
    else:
        return False
