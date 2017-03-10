from . import Command, register
from ..models import listUsers, initAlembic


@register
class ListUsers(Command):
    NAME = "listusers"
    HELP = "List users in the database"


    def _run(self, args=None):
        initAlembic()

        args = args or self.args

        print("Users:")
        for uname, roles in listUsers(self.db_session):
            print("   %s:  roles: %s" % (uname, ", ".join(roles)))
        return 0
