import argparse

from nicfit import command
import mishmash.config
from mishmash.core import Command

from .. import models, auth
from ..models import User


@command.register
class ListUsers(Command):
    NAME = "listusers"
    HELP = "List users in the database"


    def __init__(self, subparsers=None):
        super().__init__(subparsers)


    def _run(self, args=None):
        args = args or self.args

        print("Users:")
        for uname, roles in models.listUsers(self.db_session):
            print("   %s:  roles: %s" % (uname, ", ".join(roles)))
        return 0
