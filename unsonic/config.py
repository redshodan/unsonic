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
