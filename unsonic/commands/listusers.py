from nicfit import command
from mishmash.core import Command

from .. import models


@command.register
class ListUsers(Command):
    NAME = "listusers"
    HELP = "List users in the database"


    def _run(self, args=None):
        args = args or self.args

        print("Users:")
        for uname, roles in models.listUsers(self.db_session):
            print("   %s:  roles: %s" % (uname, ", ".join(roles)))
        return 0
