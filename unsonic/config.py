import os
import configparser

# This needs to be very early in the import sequence so the monkeypatch
# works right.
import mishmash
from mishmash.config import Config as MishConfig


class HereConfig(MishConfig):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        # Here
        here = "/".join(os.path.dirname(__file__).split("/")[:-1])
        self.set(configparser.DEFAULTSECT, "here", here)
        if filename:
            # Cfghere
            cfghere = os.path.dirname(os.path.abspath(filename))
            self.set(configparser.DEFAULTSECT, "cfghere", cfghere)


    def get(self, section, key, **kwargs):
        val = super().get(section, key, **kwargs)
        if val and "%(here)s" in val:
            return val.replace("%(here)s",
                               super().get(configparser.DEFAULTSECT, "here"))
        elif val and "%(cfghere)s" in val:
            return val.replace("%(cfghere)s",
                               super().get(configparser.DEFAULTSECT, "cfghere"))
        else:
            return val


mishmash.config.Config = HereConfig
