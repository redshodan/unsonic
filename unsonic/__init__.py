import os, configparser

# This needs to be very early in the import sequence so the monkeypatch
# works right.
import mishmash
from mishmash.config import Config as MishConfig

class HereConfig(MishConfig):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        here = "/".join(os.path.dirname(__file__).split("/")[:-1])
        self.set(configparser.DEFAULTSECT, "here", here)

    def get(self, section, key, **kwargs):
        val = super().get(section, key, **kwargs)
        if val and "%(here)s" in val:
            return val.replace("%(here)s",
                               super().get(configparser.DEFAULTSECT, "here"))
        else:
            return val

mishmash.config.Config = HereConfig


from . import models, log, auth


# Used by pkg_resources and Pyramid to load the webapp
from .web import main


HERE = os.getcwd()
