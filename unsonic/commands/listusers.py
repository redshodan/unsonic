from . import Command, register
from ..models import listUsers


@register
class ListUsers(Command):
    NAME = "listusers"
    HELP = "List users in the database"


    def _run(self, args=None):
        super()._run()

        args = args or self.args

        print("Users:")
        for uname, roles in listUsers(self.db_session):
            print("   %s:  roles: %s" % (uname, ", ".join(roles)))
        return 0
