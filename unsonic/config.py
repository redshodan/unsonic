import os
import configparser

# This needs to be very early in the import sequence so the monkeypatch
# works right.
import mishmash
from mishmash.config import Config as MishConfig


CONFIG = None


class HereConfig(MishConfig):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        global CONFIG
        CONFIG = self
        # %(install)s
        install = "/".join(os.path.dirname(__file__).split("/")[:-1])
        self.set(configparser.DEFAULTSECT, "install", install)
        if filename:
            # %(here)s
            here = os.path.dirname(os.path.abspath(filename))
            self.set(configparser.DEFAULTSECT, "here", here)
        else:
            self.set(configparser.DEFAULTSECT, "here", install)


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
