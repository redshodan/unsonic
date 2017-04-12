from . import Command, register
from ..models import User, initAlembic


@register
class DelUser(Command):
    NAME = "deluser"
    HELP = "Delete a user from the database."


    def _initArgParser(self, parser):
        parser.add_argument("username", nargs=1, help="users name")


    def _run(self, args=None):
        initAlembic(self.config.get("mishmash", "sqlalchemy.url"))
        args = args or self.args

        res = self.db_session.query(User).filter(User.name == args.username[0])
        if res.one_or_none():
            res.delete()
            print("Deleted user '%s'." % args.username[0])
            return 0
        else:
            print("User '%s' doesn't exists." % args.username[0])
            return -1
