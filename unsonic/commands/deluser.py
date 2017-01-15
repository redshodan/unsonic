import argparse

import mishmash.config
from mishmash.commands import command

from .. import models, auth
from ..models import User


@command.register
class DelUser(command.Command):
    NAME = "deluser"

    def __init__(self, subparsers=None):
        super().__init__("Delete a user from the database.", subparsers)
        self.parser.add_argument("username", nargs=1, help="Username")


    def _run(self, args=None):
        args = args or self.args

        res = self.db_session.query(User).filter(User.name == args.username[0])
        if res.one_or_none():
            res.delete()
            print("Deleted user '%s'." % args.username[0])
            return 0
        else:
            print("User '%s' doesn't exists." % args.username[0])
            return -1
