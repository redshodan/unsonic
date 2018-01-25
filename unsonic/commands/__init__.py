# flake8: noqa: F401

import sys

from nicfit.command import register
from mishmash import core

from unsonic import __main__


class Command(core.Command):
    CFG_NEEDED = True
    DB_NEEDED = True
    
    def _run(self, args=None):
        if self.CFG_NEEDED:
            if not __main__.APP.cfg_found:
                print("Could not find a standardly located config. "
                      "You must specify the config file with -c argument, "
                      "example: unsonic -c /etc/unsonic.ini ...")
                sys.exit(-1)
            if self.DB_NEEDED:
                initAlembic(self.config.get("mishmash", "sqlalchemy.url"))


from ..models import initAlembic

from .adduser import AddUser
from .config import Config
from .deluser import DelUser
from .listusers import ListUsers
from .password import Password
from .serve import Serve
from .man import Man
from .install import Install
