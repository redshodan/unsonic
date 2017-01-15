import argparse

import mishmash.config
from mishmash.commands import command

from .. import models, auth
from ..models import User


@command.register
class ListUsers(command.Command):
    NAME = "listusers"

    def __init__(self, subparsers=None):
        super().__init__("List users in the database", subparsers)


    def _run(self, args=None):
        args = args or self.args

        print("Users:")
        for uname, roles in models.listUsers(self.db_session):
            print("   %s:  roles: %s" % (uname, ", ".join(roles)))
        return 0
