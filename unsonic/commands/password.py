import argparse

import mishmash.config
from mishmash.commands import command

from .. import models, auth
from ..models import User


@command.register
class Password(command.Command):
    NAME = "password"

    def __init__(self, subparsers=None):
        super().__init__("Change a users password.", subparsers)
        self.parser.add_argument("username", nargs=1, help="Username")
        self.parser.add_argument("password", nargs=1, help="Password")


    def _run(self, args=None):
        args = args or self.args
        if models.setUserPassword(self.db_session, args.username[0],
                                  args.password[0]):
            print("Password set for '%s'." % args.username[0])
            return 0
        else:
            print("User '%s' not found." % args.username[0])
            return -1
