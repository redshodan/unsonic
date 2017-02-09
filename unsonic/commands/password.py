from nicfit import command
from mishmash.core import Command

from .. import models


@command.register
class Password(Command):
    NAME = "password"
    HELP = "Change a users password."


    def _initArgParser(self, parser):
        parser.add_argument("username", nargs=1, help="Username")
        parser.add_argument("password", nargs=1, help="Password")


    def _run(self, args=None):
        args = args or self.args
        if models.setUserPassword(self.db_session, args.username[0],
                                  args.password[0]):
            print("Password set for '%s'." % args.username[0])
            return 0
        else:
            print("User '%s' not found." % args.username[0])
            return -1
