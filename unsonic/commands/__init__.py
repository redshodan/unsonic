# flake8: noqa: F401

from nicfit.command import register
from mishmash import core


class Command(core.Command):
    def _run(self, args=None):
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
